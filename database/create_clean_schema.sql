
DROP TABLE IF EXISTS campaign_emails CASCADE;
DROP TABLE IF EXISTS marketing_campaigns CASCADE;
DROP TABLE IF EXISTS rfm CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    country TEXT,
    name TEXT,
    email TEXT
);

CREATE TABLE transactions (
    invoice TEXT,
    invoice_date TIMESTAMP,
    stock_code TEXT,
    quantity INTEGER,
    price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    customer_id BIGINT
);

CREATE TABLE items (
    stock_code TEXT,
    description TEXT,
    price DECIMAL(10,2)
);

CREATE TABLE rfm (
    customer_id BIGINT,
    recency INTEGER,
    frequency INTEGER,
    monetary DECIMAL(10,2),
    r INTEGER,
    f INTEGER,
    m INTEGER,
    rfm_score INTEGER,
    segment TEXT
);

CREATE TABLE marketing_campaigns (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE campaign_emails (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES marketing_campaigns(id),
    customer_id BIGINT REFERENCES customers(customer_id),
    email_subject TEXT,
    email_body TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_customer_id ON customers(customer_id);
CREATE INDEX idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX idx_transactions_stock_code ON transactions(stock_code);
CREATE INDEX idx_items_stock_code ON items(stock_code);
CREATE INDEX idx_rfm_customer_id ON rfm(customer_id);