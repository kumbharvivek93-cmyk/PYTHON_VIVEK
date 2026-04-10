from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from starlette.requests import Request


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "knowledge_base.json"
SUPPORTED_DOMAINS = {
    "banking",
    "healthcare",
    "education",
    "e-commerce",
    "government",
    "all",
}
SUPPORTED_LANGUAGES = {"en", "hi", "es", "fr", "auto"}
TOKEN_PATTERN = re.compile(r"[a-zA-Z]+")
SUPPORT_INTENT_KEYWORDS = {
    "account",
    "appeal",
    "application",
    "appointment",
    "bank",
    "card",
    "certificate",
    "claim",
    "delivery",
    "document",
    "documents",
    "exam",
    "foreclosure",
    "hospital",
    "insurance",
    "invoice",
    "loan",
    "logistics",
    "lms",
    "order",
    "payment",
    "policy",
    "portal",
    "refund",
    "registration",
    "reject",
    "rejected",
    "replacement",
    "reschedule",
    "return",
    "service",
    "sla",
    "student",
    "ticket",
    "tracking",
    "transaction",
    "verification",
}


class Message(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=2)
    domain: str = "all"
    language: str = "en"
    history: list[Message] = Field(default_factory=list)
    include_voice: bool = False


class SourceSnippet(BaseModel):
    source_id: str
    title: str
    domain: str
    score: float
    excerpt: str


class ToolTrace(BaseModel):
    tool: str
    status: str
    detail: str


class ChatResponse(BaseModel):
    answer: str
    detected_language: str
    sentiment: str
    escalation_required: bool
    tools_used: list[ToolTrace]
    sources: list[SourceSnippet]
    voice: dict[str, Any]


@dataclass
class KnowledgeDocument:
    source_id: str
    domain: str
    title: str
    content: str
    tags: list[str]


class KnowledgeBase:
    def __init__(self, path: Path) -> None:
        raw_docs = json.loads(path.read_text(encoding="utf-8"))
        self.documents = [KnowledgeDocument(**item) for item in raw_docs]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(
            [self._searchable_text(doc) for doc in self.documents]
        )

    @staticmethod
    def _searchable_text(doc: KnowledgeDocument) -> str:
        return " ".join([doc.domain, doc.title, doc.content, " ".join(doc.tags)])

    def search(
        self,
        query: str,
        domain: str,
        limit: int = 3,
        min_score: float = 0.08,
    ) -> list[SourceSnippet]:
        similarities = cosine_similarity(
            self.vectorizer.transform([query]), self.matrix
        ).flatten()

        ranked: list[tuple[KnowledgeDocument, float]] = []
        for doc, score in zip(self.documents, similarities):
            if domain == "all" or doc.domain == domain:
                ranked.append((doc, float(score)))

        ranked.sort(key=lambda item: item[1], reverse=True)

        snippets: list[SourceSnippet] = []
        for doc, score in ranked[:limit]:
            if score < min_score:
                continue
            excerpt = doc.content[:220].strip()
            if len(doc.content) > 220:
                excerpt += "..."
            snippets.append(
                SourceSnippet(
                    source_id=doc.source_id,
                    title=doc.title,
                    domain=doc.domain,
                    score=round(score, 3),
                    excerpt=excerpt,
                )
            )
        return snippets

    def available_domains(self) -> list[str]:
        return sorted({doc.domain for doc in self.documents})


class SupportTools:
    ORDER_DB = {
        "ORD-2048": {"status": "Shipped", "eta": "2 business days"},
        "TCK-7781": {"status": "Waiting for specialist review", "eta": "Today"},
    }

    def run(self, message: str) -> list[ToolTrace]:
        traces: list[ToolTrace] = []
        lower = message.lower()
        tokens = set(TOKEN_PATTERN.findall(lower))
        ref = self._extract_reference(message)
        has_ticket_context = bool(
            {"order", "ticket", "application", "certificate", "tracking"} & tokens
        )

        if ref or has_ticket_context:
            if ref and ref in self.ORDER_DB:
                traces.append(
                    ToolTrace(
                        tool="ticket_lookup",
                        status="success",
                        detail=f"{ref}: {self.ORDER_DB[ref]['status']} | ETA: {self.ORDER_DB[ref]['eta']}",
                    )
                )
            else:
                traces.append(
                    ToolTrace(
                        tool="ticket_lookup",
                        status="needs_input",
                        detail="No valid order or ticket reference found in the message.",
                    )
                )

        if {"policy", "refund", "claim", "document", "documents"} & tokens:
            traces.append(
                ToolTrace(
                    tool="policy_router",
                    status="success",
                    detail="Matched the request to the knowledge-base policy workflow.",
                )
            )

        if not traces:
            traces.append(
                ToolTrace(
                    tool="conversation_router",
                    status="success",
                    detail="Handled with retrieval-augmented response generation.",
                )
            )

        return traces

    @staticmethod
    def _extract_reference(message: str) -> str | None:
        match = re.search(r"\b(?:ORD|TCK)-\d{4,}\b", message.upper())
        return match.group(0) if match else None


class CustomerSupportAgent:
    NEGATIVE_WORDS = {
        "angry",
        "bad",
        "cancel",
        "complaint",
        "delay",
        "frustrated",
        "issue",
        "problem",
        "reject",
        "rejected",
        "refund",
        "upset",
        "worst",
    }
    POSITIVE_WORDS = {"great", "thanks", "helpful", "good", "awesome", "love"}
    LANGUAGE_HINTS = {
        "es": ("hola", "gracias", "pedido", "reembolso"),
        "hi": ("namaste", "dhanyavaad", "madad", "order"),
        "fr": ("bonjour", "merci", "commande", "remboursement"),
    }

    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        self.knowledge_base = knowledge_base
        self.tools = SupportTools()

    def reply(self, payload: ChatRequest) -> ChatResponse:
        cleaned_message = payload.message.strip()
        if len(cleaned_message) < 2:
            raise HTTPException(status_code=400, detail="Message is too short.")

        domain = self.normalize_domain(payload.domain)
        language = self.normalize_language(payload.language)

        detected_language = self.detect_language(cleaned_message, language)
        sentiment = self.detect_sentiment(cleaned_message)
        support_intent = self.is_support_query(cleaned_message, domain)
        escalation_terms = {"complaint", "legal", "manager", "urgent", "urgently", "rejected", "escalate"}
        message_tokens = set(TOKEN_PATTERN.findall(cleaned_message.lower()))
        escalation = support_intent and sentiment == "negative" and bool(message_tokens & escalation_terms)

        tool_traces = self.tools.run(cleaned_message) if support_intent else [
            ToolTrace(
                tool="conversation_router",
                status="success",
                detail="Handled as a general conversation question.",
            )
        ]
        sources: list[SourceSnippet] = []
        if support_intent:
            sources = self.knowledge_base.search(cleaned_message, domain, min_score=0.12)
            if not sources and domain != "all":
                sources = self.knowledge_base.search(cleaned_message, "all", min_score=0.12)
        answer = self.compose_answer(
            message=cleaned_message,
            domain=domain,
            language=detected_language,
            history=payload.history,
            sources=sources,
            sentiment=sentiment,
            escalation=escalation,
            tools=tool_traces,
            support_intent=support_intent,
        )

        voice_payload = {
            "stt_enabled": payload.include_voice,
            "tts_enabled": payload.include_voice,
            "recommended_stack": ["Whisper", "gTTS or Azure TTS"] if payload.include_voice else [],
        }

        return ChatResponse(
            answer=answer,
            detected_language=detected_language,
            sentiment=sentiment,
            escalation_required=escalation,
            tools_used=tool_traces,
            sources=sources,
            voice=voice_payload,
        )

    def normalize_domain(self, domain: str) -> str:
        normalized = (domain or "all").strip().lower()
        if normalized not in SUPPORTED_DOMAINS:
            return "all"
        return normalized

    def normalize_language(self, language: str) -> str:
        normalized = (language or "en").strip().lower()
        if normalized not in SUPPORTED_LANGUAGES:
            return "en"
        return normalized

    def detect_sentiment(self, message: str) -> str:
        tokens = set(TOKEN_PATTERN.findall(message.lower()))
        if tokens & self.NEGATIVE_WORDS or any(
            token.startswith(("delay", "frustrat", "reject", "urgent", "complain"))
            for token in tokens
        ):
            return "negative"
        if tokens & self.POSITIVE_WORDS:
            return "positive"
        return "neutral"

    def detect_language(self, message: str, requested_language: str) -> str:
        if requested_language and requested_language != "auto":
            return requested_language

        lower = message.lower()
        for language, hints in self.LANGUAGE_HINTS.items():
            if any(hint in lower for hint in hints):
                return language
        return "en"

    def is_support_query(self, message: str, domain: str) -> bool:
        tokens = set(TOKEN_PATTERN.findall(message.lower()))
        if self.tools._extract_reference(message):
            return True
        has_support_keywords = bool(tokens & SUPPORT_INTENT_KEYWORDS)
        if domain != "all":
            return has_support_keywords
        return has_support_keywords

    def compose_answer(
        self,
        message: str,
        domain: str,
        language: str,
        history: list[Message],
        sources: list[SourceSnippet],
        sentiment: str,
        escalation: bool,
        tools: list[ToolTrace],
        support_intent: bool,
    ) -> str:
        history_summary = ""
        if history:
            history_summary = f"The user has {len(history)} prior chat turns, so preserve context and avoid repeating solved steps. "

        source_lines = []
        for source in sources:
            source_lines.append(
                f"{source.title}: {source.excerpt}"
            )

        evidence = " ".join(source_lines) if source_lines else "No matching knowledge-base articles were retrieved."
        tool_context = " | ".join(trace.detail for trace in tools)
        is_general_query = (not support_intent) or (
            not sources and all(trace.tool == "conversation_router" for trace in tools)
        )

        api_answer = self.try_openai_response(
            message=message,
            domain=domain,
            language=language,
            history_summary=history_summary,
            evidence=evidence,
            sentiment=sentiment,
            escalation=escalation,
            tool_context=tool_context,
            is_general_query=is_general_query,
        )
        if api_answer:
            return api_answer

        response = self.compose_local_response(
            message=message,
            domain=domain,
            language=language,
            evidence=evidence,
            sentiment=sentiment,
            escalation=escalation,
            tool_context=tool_context,
            is_general_query=is_general_query,
            sources=sources,
        )
        return response

    def compose_local_response(
        self,
        message: str,
        domain: str,
        language: str,
        evidence: str,
        sentiment: str,
        escalation: bool,
        tool_context: str,
        is_general_query: bool,
        sources: list[SourceSnippet],
    ) -> str:
        if is_general_query:
            return self.compose_general_local_response(message, language)

        empathetic_openers = {
            "negative": "I can see this is frustrating, and I'll keep the next steps clear.",
            "positive": "Happy to help and keep this moving.",
            "neutral": "Here's the most relevant support guidance I found.",
        }
        language_prefix = {
            "en": "",
            "es": "Respuesta en espanol: ",
            "hi": "Hindi support summary: ",
            "fr": "Reponse en francais: ",
        }.get(language, "")

        escalation_text = (
            "I also recommend routing this to a human support specialist because the request sounds urgent or complaint-related. "
            if escalation
            else ""
        )

        if not sources:
            return (
                f"{language_prefix}{empathetic_openers[sentiment]} "
                f"{escalation_text}"
                "I need one more specific detail to give accurate next steps, such as an order ID, claim ID, student ID, or application number."
            )

        top = sources[0]
        actions: list[str] = [top.excerpt]
        if "ticket_lookup" in tool_context.lower() and "no valid" in tool_context.lower():
            actions.append("Share your order/ticket reference (example: ORD-2048 or TCK-7781) so I can check status.")
        if escalation:
            actions.append("Escalate this to a human specialist because urgency/complaint language is present.")

        return (
            f"{language_prefix}{empathetic_openers[sentiment]} "
            f"{' '.join(actions)}"
        )

    def compose_general_local_response(self, message: str, language: str) -> str:
        lower = message.lower()
        tokens = set(TOKEN_PATTERN.findall(lower))

        if {"tense", "tenses", "grammar"} & tokens:
            return (
                "Start with just 3 tenses first: present simple, past simple, and future simple. "
                "Use this 20-minute routine daily: 5 minutes rule, 10 minutes examples, 5 minutes speaking. "
                "Rule shortcut: present = habit/fact, past = finished action, future = plan/prediction. "
                "Make 3 sentences per tense about your own life, then read them aloud. "
                "After 7 days, add present continuous and present perfect."
            )

        if "how do i learn" in lower or "how can i learn" in lower:
            return (
                "Use a simple loop: learn one small concept, practice with 5 examples, then explain it in your own words. "
                "Study in short daily sessions (20-30 minutes), track mistakes, and revise after 1 day, 3 days, and 7 days. "
                "If you tell me the exact topic, I can give you a step-by-step plan."
            )

        if {"study", "learn", "improve"} & tokens:
            return (
                "Break the topic into small parts and practice one part at a time. "
                "Use active recall (answer without looking) and spaced repetition (review after gaps). "
                "Do one focused practice session daily and measure progress with a short weekly test."
            )

        return (
            "I can help with this. Share your exact goal and your current level, and I will give you a clear step-by-step answer."
        )

    def try_openai_response(
        self,
        message: str,
        domain: str,
        language: str,
        history_summary: str,
        evidence: str,
        sentiment: str,
        escalation: bool,
        tool_context: str,
        is_general_query: bool,
    ) -> str | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        try:
            from openai import OpenAI
        except ImportError:
            return None

        if is_general_query:
            prompt = (
                "You are a concise, helpful general-purpose assistant. "
                "Answer the user's question directly. "
                "Do not force customer-support workflows when they are not relevant. "
                "Never mention metadata, routing, tools, domains, confidence, or internal reasoning. "
                "Return only the final user-facing answer text. "
                f"Respond in language code '{language}'. "
                f"{history_summary}"
                f"User message: {message}"
            )
        else:
            prompt = (
                "You are a production customer-support AI assistant. "
                "Use the retrieved knowledge faithfully, keep answers concise, and mention when escalation is appropriate. "
                "Never mention metadata, routing, tools, domains, confidence, or internal reasoning. "
                "Return only the final user-facing answer text. "
                f"Respond in language code '{language}'. "
                f"Sentiment: {sentiment}. Escalation needed: {escalation}. "
                f"{history_summary}"
                f"Domain: {domain}. "
                f"Tool context: {tool_context}. "
                f"Knowledge snippets: {evidence}. "
                f"User message: {message}"
            )

        try:
            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                input=prompt,
            )
            return response.output_text.strip()
        except Exception:
            return None


app = FastAPI(
    title="AI Customer Support Agent",
    description="LLM-powered customer support assistant with retrieval, sentiment detection, and tool routing.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
knowledge_base = KnowledgeBase(DATA_FILE)
agent = CustomerSupportAgent(knowledge_base)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "domains": knowledge_base.available_domains() + ["all"],
            "languages": [
                ("en", "English"),
                ("hi", "Hindi"),
                ("es", "Spanish"),
                ("fr", "French"),
                ("auto", "Auto Detect"),
            ],
            "sample_prompts": [
                "My order ORD-2048 is late. What should support do next?",
                "My medical claim was rejected even after I uploaded the invoice.",
                "I cannot complete exam registration after payment.",
                "My certificate application is still under verification after the SLA.",
            ],
        },
    )


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-customer-support-agent"}


@app.get("/api/knowledge")
async def list_knowledge(domain: str = "all") -> dict[str, Any]:
    normalized_domain = agent.normalize_domain(domain)
    docs = [
        {
            "source_id": doc.source_id,
            "title": doc.title,
            "domain": doc.domain,
            "tags": doc.tags,
        }
        for doc in knowledge_base.documents
        if normalized_domain == "all" or doc.domain == normalized_domain
    ]
    return {"count": len(docs), "domain": normalized_domain, "items": docs}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    return agent.reply(payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
