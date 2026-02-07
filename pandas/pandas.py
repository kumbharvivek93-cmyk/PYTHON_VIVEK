# import pandas 
# # l=[1,2,3,4,5]
# # series=pandas.Series(l , index=["a","b","c","d","e"]) # Series is a constructor
# # # print(series.loc["a"])  
# # # # print(series.iloc[0])
# # # print(series[series>2])      # use values for filtration

# # # import pandas as pd
# # # calories={
# # # #     "Day 1":1540,
# # # #     "Day 2":1800,
# # # #     "Day 3":1300
# # # # }

# # # # series=pd.Series(calories)
# # # # print(series[series<1500])


# # # #  DataFrame
# # # # import pandas as pd

# # # # pokimons={
# # # #     "names":["pikachu","onix","spongbob","bublbsour"],
# # # #     "powers":[100,200,300,400]
# # # # }

# # # # df=pd.DataFrame(pokimons ,index=range(1,5))   # call the constructor and then pass the arrguments
# # # # df["HP"]=[120,150,250,135]  # as like this we can add one column
# # # # # print(df)
# # # # # to create one new row we have to create a new dictionary and concatinate them both 
# # # # dew_dict=pd.DataFrame([{"names":"Greyninja","powers":750 ,"HP":350}])
# # # # df=pd.concat([df,dew_dict])
# # # # print(df)

# # # import pandas as pd

# # # pokimons ={
# # #     "names":["pikachuu","Gengar","onix"],
# # # #     "powers":[130,155,110],
# # # #     "hp":[135,120,177]
# # # # }
# # # # df=pd.DataFrame(pokimons)
# # # # print(df["powers"]>125)

# # # # import pandas as pd  
# # # # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv") # read csv function takes the link or the name of the csv file 
# # # # print(df.iloc[1:10:2, 2:5]) # to select multiple columns

# # # # # Filtration
# # # # import pandas as pd
# # # # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")

# # # # Power_pokemon=df[df["Power"]>160] # use of subscript operator is must []
# # # # print(Power_pokemon)   # this is called as filtration


# # # import pandas as pd
# # # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")
# # # print(df.mean(numeric_only=True))
# # # # this code tells pands show the mean of only those coloumns contaning the numeric data in the data_Frame

# # import pandas as pd
# # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")
# # # print(df.sum(numeric_only=True))
# # # # this code tells pands show the sum of only those coloumns contaning the numeric data in the data_Frame
# # # import pandas as pd
# # # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")
# # # print(df.min(numeric_only=True))
# # # # this code tells pands show the min of only those coloumns contaning the numeric data in the data_Frame
# # # import pandas as pd
# # # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")
# # # print(df.max(numeric_only=True))
# # # # this code tells pands show the max of only those coloumns contaning the numeric data in the data_Frame
# # # import pandas as pd
# # # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")
# # # print(df.median(numeric_only=True))
# # # # this code tells pands show the median of only those coloumns contaning the numeric data in the data_Frame

# # # print(df['Speed'].sum())
# # group= df.groupby("Type")
# # print(group["Power"].mean())  # good level syntax & understanding

# # import pandas as pd
# # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")
# # # df=df.drop(columns=["Legendary","Name"])   # dropping some data
# # # print(df)
# # # df["Name"]=df["Type"].replace({"Water" : "bhadva"})
# # # print(df["Name"])
# # # print(df.to_string())
# # df=df.drop(columns=["Name"])
# # print(df)

# # import pandas as pd
# # df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")
# # # print(df)
# # # df["Type"]=df["Type"].replace({"Fire" : " AAG"})   # to replace
# # # print(df)   
# # df["Legendary"]=df["Legendary"].replace({False:True})   # this is how we can standardize the string or the name col.
# # print(df)

# # # to change the data type we use the astype() 


# # common vivewing functons in pandas

# import pandas as pd
# df=pd.read_csv("/home/vivek2006/Desktop/python/pokemon.csv")
# # print(df.info())  # we can also find the memory storage
# # 
# # selecting the data
# # print(df.loc["Pokemon2"])   A good syntax


# # data filtering
# # print(df[df["HP"]>180])  # by accessing the DataFrame and a common syntax

# # THE MOST IMPORTANT DATA CLEANING ABOUT SEVENTY-FIVE PERCENTAGE OF WORK IS DEPENDED ON IT

# # df["Name"]=df["Name"].replace({"Pokemon2":"pikachuu"})
# # print(df["Name"])
# df["Col2"] = df["Col2"].fillna("Fire")

# # # df.
# # df.loc[2]="pikachuuu" 
# # df.loc[2]["Type"]="Electric"
# print(df.iloc[1:11:1 , 2:5])
# import pandas as pd
# df=pd.read_csv("pokea.csv")
# # print(df)
# # df["Col2"]=df["Col2"].replace({"NaN":"Fire"})
# # df.iloc[:, 1] = df.iloc[:, 1].fillna("Fire")
# df["Col2"]=df["Col2"].fillna("Fire")
# # #  iloc always uses the square brackets not the parenthesis
# # # print(df.iloc[1:105:1 ,1:4].to_string())
# # df["Col3"]=df["Col3"].fillna("vivek.G")
# # print(df)

# # import pandas as pd
# # df=pd.read_csv("pokemon.csv")
# # # df=df.set_index('Date')
# # df=df.plot(kind='bar',subplots=True)
# # print(df)
# # # print(df["HP"].mean(numeric_only=True))

# # # import pandas as pd
# # # # df=pd.read_excel("/home/vivek2006/Downloads/M-I ESE (2025-26) Question Paper Format-3.xlsx")
# # # # print(df.iloc[0:28:1 ,5:5])
 
# # # # NOW DATA CLEANING !!
# # # import pandas as pd
# # # df=pd.read_csv("/home/vivek2006/Desktop/python/Datacleeanin.csv")

# # # # df["Salary"]=df["Salary"]
# # # df["Email"]=df["Email"].fillna("Not updated")
# # # df["Age"]=df["Age"].clip(lower=1 , upper=99)
# # # df["Age"]=df["Age"].fillna("Not updated")
# # # df["Full_Name"]=df["Full_Name"].fillna("Not updated")


# # # print(df["Salary"].dtype)
# # # df.to_csv("/home/vivek2006/Desktop/python/Datacleeanin.csv", index=False)

# # import pandas as pd
# # df=pd.read_csv("/home/vivek2006/Desktop/python/pandaspra.csv")
# # df=df.drop_duplicates()
# # df["Country"]=df["Country"].astype(str)
# # df["Country"]=df["Country"].str.strip()
# # df["Country"]=df["Country"].str.upper()
# # df["Country"]=df["Country"].fillna("empty",c)


# # print(df.to_string())


# # import pandas as pd
# # df=pd.read_csv("/home/vivek2006/Desktop/python/pandaspra.csv",index_col="order_id")
# # df.columns=df.columns.str.strip()   # coloumn handling
# # df.columns=df.columns.str.upper()
# # # #  data type fixing
# # df['PRICE'] = pd.to_numeric(df['PRICE'].astype(str).str.replace('$', '', regex=False),errors='coerce')
# # df["TOTAL"]=pd.to_numeric(df["TOTAL"],errors="coerce")
# # df['TOTAL']=df['TOTAL'].abs()
# # df['QUANTITY']=df['QUANTITY'].replace()
# # df['QUANTITY']=pd.to_numeric(df['QUANTITY'],errors='coerce')
# # # df["TOTAL"]=df['TOTAL'].fillna(df["PRICE"]*df["QUANTITY"])
# # df['QUANTITY']=df['QUANTITY'].astype(int,errors="ignore")
# # print(df['QUANTITY'].dtype)



# # print(df.to_string())
# # #we shall go with the prefferd secquence that first load the csv
# # #second= colounm formatiing and handling ( upper(), str,strip())
# # #third=drop_duplicates
# # # fourth = handel the data type
# # # fifth= claen each col.

# # import pandas as pd
# # df=pd.read_csv("/home/vivek2006/Desktop/python/pandaspra.csv")
# # df["Quantity"]=df["Quantity"].replace("three","3")
# # df["Quantity"]=pd.to_numeric(df["Quantity"],errors="coerce")
# # print(df["Quantity"].dtype)


# # rivision of pandas 
# import pandas as pd
# df=pd.read_csv("/home/vivek2006/Desktop/python/pandaspra.csv")
# df.columns=df.columns.str.strip()
# df.columns=df.columns.str.capitalize()
# # df["Order_date"]=pd.to_datetime(df["Order_date"],errors="coerce",yearfirst=True,dayfirst=False)
# df["Total"]=pd.to_numeric(df["Total"])
# # df["Price"]=pd.to_numeric(df["Price"])
# df["Order_id"]=pd.to_numeric(df["Order_id"])
# df["Price"].iloc[0]=1200
# df["Price"]=pd.to_numeric(df["Price"],errors="coerce")
# df["Quantity"].iloc[10]=3
# df["Quantity"]=pd.to_numeric(df["Quantity"])
# df["Age"].iloc[2]=30
# df["Age"]=pd.to_numeric(df["Age"],errors="coerce") # all the col. are setted to their data types
# df["Country"]=df["Country"].str.strip().str.upper()
# df["Country"]=df["Country"].fillna("NOT UPDATED")
# df["Total"]=df["Total"].fillna(df["Price"]*df["Quantity"]) # finded the missing total
# df["Total"]=df["Total"].abs()
# df["Quantity"]=df["Quantity"].abs()
# df["Product"]=df["Product"].fillna("INVALID ORDER")
# df=df.drop_duplicates()
# df["Age"]=df["Age"].fillna("NOT UPDATED")
# df["Customer name"]=df["Customer name"].str.upper().str.strip()
# df.to_csv("/home/vivek2006/Desktop/python/pandaspra.csv", index=False)




# print(df.to_string())\


# import pandas as pd
# df=pd.read_csv("/home/vivek2006/Desktop/python/panda_pra_2.csv")
# df.columns=df.columns.str.strip()
# df.columns=df.columns.str.capitalize()
# df["Purchase_amount"]=pd.to_numeric(df["Purchase_amount"], errors="coerce")
# df["Country"]=df["Country"].str.upper()
# df["Country"]=df["Country"].str.strip()
# df["Signup_date"]=pd.to_datetime(df["Signup_date"],errors="coerce")
# df["Email"]=df["Email"].str.strip()
# df["Email"].iloc[2]="INVALID EMAIL"
# df["Gender"]=df["Gender"].astype(str)
# print(df["Gender"].dtype)




# # print(df.to_string())


# import pandas as pd
# df=pd.read_csv("/home/vivek2006/pandapra3.csv")   # step 1 loading the CSV
# df.columns=df.columns.str.strip().str.capitalize()  # step 2 coloumn handing and standerdization
# df=df.drop_duplicates()  # step  removing the duplicates
# df["Quantity"].iloc[7]=1
# df["Quantity"]=pd.to_numeric(df["Quantity"])
# df["Product"]=df["Product"].astype("string")    # step3 data type conversioion 
# df["City"]=df["City"].astype("string")
# df["Gender"]=df["Gender"].astype("string")
# df["Age"].iloc[5]=30
# df["Age"]=pd.to_numeric(df["Age"],errors="coerce")
# df["Customer_name"]=df["Customer_name"].astype("string")
# df["Email"]=df["Email"].fillna("NOT UPDATED")
# df["Order_date"]=pd.to_datetime(df["Order_date"],errors="coerce",dayfirst=True)
# df["City"]=df["City"].str.strip().str.capitalize()
# df["Customer_name"]=df["Customer_name"].str.strip().str.capitalize()
# df["Gender"]=df["Gender"].str.strip().str.upper()



# df["Customer_name"]=df["Customer_name"].fillna("UNKNOWN")
# # print(df["Age"].dtype)

# print(df.to_string())
# df.to_csv("/home/vivek2006/pandapra3.csv",index=False)
# above code is based on morden guidelines of ml


# AFTER FIRST SEM RIVISION OF PANDAS 

# 1.SERIES

# import pandas as pd
# l=[10,20,30,40,50]   # using the iloc needs to use of the square brackets
# series=pd.Series(l)
# series.iloc[3]=100
# print(series[series>20])


# 2.DATAFRAME

# import pandas as pd
# pokemons={
#     'names':["pikachu","buldbsour","greyninja"],
#     "HP":[80,85,154]
# }
# df=pd.DataFrame(pokemons)
# print(df[df["HP"]>81])

# b) Aggrigate functions
# DONE


# import pandas as pd
# df=pd.read_csv("/home/vivek2006/Desktop/python/pandas_pra4,csv")
# df.columns=df.columns.str.strip().str.capitalize()
# df=df.drop_duplicates()
# df["Purchased"]=df["Purchased"].astype("string")
# df["Salary"]=pd.to_numeric(df["Salary"],errors="coerce")
# df["Country"]=df["Country"].astype("string")
# df["Signup_date"]=pd.to_datetime(df["Signup_date"],errors="coerce",dayfirst=True)
# df["Age"]=pd.to_numeric(df["Age"],errors="coerce")
# df["Gender"]=df["Gender"].astype("string")
# df["Name"]=df["Name"].astype("string")
# df["Purchased"]=df["Purchased"].str.strip()
# df["Purchased"]=df["Purchased"].replace({"Y":"YES","N":"NO","TRUE":"YES","FALSE":"NO"})      # before using the replace function on a col. we first str.strip the extra spaces and look for a clear and good exactmatching format
# df["Purchased"]=df["Purchased"].str.upper()
# df["Country"]=df["Country"].str.upper()
# df["Country"]=df["Country"].fillna("not_updated")
# df["Country"].iloc[12]="not updated"
# df["Gender"]=df["Gender"].str.upper().str.strip()
# df["Gender"]=df["Gender"].replace({"M":"MALE","F":"FEMALE"})
# df["Age"]=df["Age"].abs().fillna(df["Age"].mean(numeric_only=True))
# # df["Age"]=df["Age"].clip(upper=30,lower=30)
# df["Name"]=df["Name"].str.capitalize().str.strip()

# df.to_csv("/home/vivek2006/Desktop/python/pandas_pra4,csv",index=False)
# print(df.to_string())

# #  Data cleaning final boss csv 
# import pandas as pd
# df=pd.read_csv("/home/vivek2006/Desktop/python/ecommerce_verydirty_csv_filanboss.csv")
# df.columns=["customer_name","Email","Age","Gender","Order_date","signup_date","Product","Quantity","Unit_price","Subtotal","Total","payment_status","Country","Note"]
# df.columns=df.columns.str.strip().str.capitalize()
# df=df.drop_duplicates(subset=["Email"])
# df["Note"]=df["Note"].astype("string")
# df["Country"]=df["Country"].astype("string")
# df["Payment_status"]=df["Payment_status"].astype("string")


# print(df["Payment_status"].dtype)


# import pandas as pd
# import matplotlib.pyplot as plt

# df=pd.read_csv("/home/vivek2006/Desktop/python/Datacleeanin.csv")
# df["Salary"]=pd.to_numeric(df["Salary"],errors="coerce")
# df["Join_Date"]=pd.to_datetime(df["Join_Date"],dayfirst=False,errors="coerce")
# df["Age"]=pd.to_numeric(df["Age"],errors="coerce")
# df["City"]=df["City"].astype("string")
# df["City"]=df["City"].str.capitalize()
# print(df["City"].dtype)
# print(df.to_string())

# series=pd.Series(df["City"])
# series.loc[3]="Baramati"
# print(series)

# 2. DataFrame
# print(df.mean(numeric_only=True))
# print("")
# print(df.sum(numeric_only=True))
# print("")

# print(df.min(numeric_only=True))
# print("")

# print(df.max(numeric_only=True))
# print("")

# print(df.median(numeric_only=True))

# # print(df.to_string())
# For single coluum also we can we aggrigate functions
# print(df["Age"].sum(numeric_only=True))
# group=df.groupby("Age")
# print(group[25])
