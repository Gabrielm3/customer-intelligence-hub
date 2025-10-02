import pandas as pd
from faker import Faker
import random
from datetime import datetime


def preprocess_data(df):
    df_clean = df.drop_duplicates(['Invoice', 'StockCode'])

    df_clean = df_clean[~df_clean['Invoice'].str.startswith('C')]
    df_clean = df_clean[~df_clean['Invoice'].str.startswith('A')]

    df_clean.dropna(subset=['Invoice', 'StockCode', 'InvoiceDate', 'Price', 'Customer ID'], how='any', inplace=True)


    df_clean['TotalPrice'] = round(df_clean['Quantity'] * df_clean['Price'], 2)

    df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'], format="mixed")
    df_clean['Customer ID'] = df_clean['Customer ID'].astype(int)
    df_clean['Quantity'] = df_clean['Quantity'].astype(int)

    return df_clean


def generate_fake_customer_data(customer_id, country):
    fake = Faker()
    Faker.seed(int(customer_id))
    random.seed(int(customer_id))

    country_locales = {
        'United Kingdom': 'en_GB',
        'France': 'fr_FR',
        'Germany': 'de_DE',
        'Spain': 'es_ES',
        'Netherlands': 'nl_NL',
        'Norway': 'no_NO',
        'Switzerland': 'de_CH',
        'Poland': 'pl_PL',
        'Australia': 'en_AU',
        'EIRE': 'en_GB',  
    }

    locale = country_locales.get(country, 'en_US') 
    fake = Faker(locale)
    Faker.seed(int(customer_id))

    name = fake.name()
    email_name = name.lower().replace(' ', '.').replace("'", "")
    email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com']
    email_domain = random.choice(email_domains)
    email = f"{email_name}@{email_domain}"

    return name, email


def generate_core_tables(df_clean):
    print("Generating core tables...")
    transaction_cols = ['Invoice', 'InvoiceDate', 'StockCode', 'Quantity', 'Price', 'TotalPrice', 'Customer ID']

    transactions = df_clean[transaction_cols]

    items = df_clean[['StockCode', 'Description', 'Price']].drop_duplicates(subset=['StockCode'])

    customers = df_clean[['Customer ID', 'Country']].drop_duplicates(subset=['Customer ID'])

    customers[['Name', 'Email']] = customers.apply(
        lambda row: generate_fake_customer_data(row['Customer ID'], row['Country']),
        axis=1,
        result_type='expand'
    )

    return transactions, items, customers


def generate_rfm(transactions):
    print("Generating RFM table...")
    rfm = transactions.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (pd.to_datetime("2012-01-01") - x.max()).days,  # Recency
        'Customer ID': 'count',  
        'TotalPrice': 'sum'
    }).rename(columns={
        'InvoiceDate': 'recency',
        'Customer ID': 'frequency',
        'TotalPrice': 'monetary'
    })

    rfm['R'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1]).astype(int)
    rfm['F'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
    rfm['M'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5]).astype(int)

    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

    def assign_segment(score):
        if score == '555':
            return 'Champion'
        elif score[0] == '5':
            return 'Recent Customer'
        elif score[1] == '5':
            return 'Frequent Buyer'
        elif score[2] == '5':
            return 'Big Spender'
        elif score[0] == '1':
            return 'At Risk'
        else:
            return 'Others'

    rfm['Segment'] = rfm['RFM_Score'].apply(assign_segment)

    return rfm


def sample_data(
        customers: pd.DataFrame, 
        transactions: pd.DataFrame, 
        items: pd.DataFrame, 
        rfm: pd.DataFrame,
        sample_size: int = 100):
    print("Sampling data...")
    sampled_customers = customers.sample(n=sample_size, random_state=42)
    sampled_transactions = transactions[transactions['Customer ID'].isin(sampled_customers['Customer ID'])]
    sampled_items = items[items['StockCode'].isin(sampled_transactions['StockCode'])]
    sampled_rfm = rfm[rfm.index.isin(sampled_customers['Customer ID'])]

    return sampled_transactions, sampled_items, sampled_customers, sampled_rfm


def export_data(transactions: pd.DataFrame, items: pd.DataFrame, customers: pd.DataFrame, rfm: pd.DataFrame):
    print("Exporting data...")
    transactions.to_csv("data/transactions.csv", index=False)
    items.to_csv("data/items.csv", index=False)
    customers.to_csv("data/customers.csv", index=False)
    rfm.reset_index().to_csv("data/rfm.csv", index=False)


def main():
    df = pd.read_csv("data/online_retail_II_2010-2011.csv")

    df_clean = preprocess_data(df)

    transactions, items, customers = generate_core_tables(df_clean)

    rfm = generate_rfm(transactions)

    sampled_transactions, sampled_items, sampled_customers, sampled_rfm = sample_data(customers, transactions, items, rfm, sample_size=100)

    export_data(sampled_transactions, sampled_items, sampled_customers, sampled_rfm)

    print("Data exported to /data")


if __name__ == "__main__":
    main()
