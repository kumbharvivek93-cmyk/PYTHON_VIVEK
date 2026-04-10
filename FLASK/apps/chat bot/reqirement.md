# AI Customer Support Agent

An LLM-powered customer support chatbot starter built with FastAPI and a lightweight retrieval pipeline. The app is designed for project/demo use across banking, healthcare, education, e-commerce, and government-service domains.

## What It Includes

- FastAPI backend with `/api/chat`, `/api/health`, and `/api/knowledge`
- Retrieval-Augmented Generation flow using a local knowledge base and TF-IDF search
- Optional OpenAI integration through `OPENAI_API_KEY`
- Sentiment detection and human escalation flags
- Multi-domain and multi-language request handling
- Voice chatbot integration hooks for STT/TTS-ready payloads
- Simple agent-style tool traces for ticket lookup and policy routing
- Responsive web UI for demos and submissions

## Project Structure

```text
c_c/
|-- app.py
|-- data/
|   |-- knowledge_base.json
|-- requirements.txt
|-- static/
|   |-- style.css
|-- templates/
|   |-- index.html
`-- README.md
```

## Run Locally

1. Activate the virtual environment:

```bash
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: configure OpenAI for real LLM responses:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4.1-mini"
```

4. Start the server:

```bash
uvicorn app:app --reload
```

5. Open `http://127.0.0.1:8000`

## Suggested Extensions

- Replace the local TF-IDF retriever with FAISS or Pinecone
- Swap the handcrafted tool router for LangChain or LlamaIndex agents
- Add Whisper-based speech-to-text and a TTS provider
- Connect ticket/order lookups to a real SQL or REST backend
- Add authentication, audit logs, and conversation persistence

## Example Payload

```json
{
  "message": "My order ORD-2048 is delayed and I want to know the refund policy.",
  "domain": "e-commerce",
  "language": "en",
  "include_voice": true,
  "history": []
}
```
