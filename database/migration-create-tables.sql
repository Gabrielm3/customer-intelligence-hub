create table public.customers (
  "Customer ID" bigint not null,
  "Country" text null,
  "Name" text null,
  "Email" text null,
  constraint customers_pkey primary key ("Customer ID")
) TABLESPACE pg_default;

ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

create table public.transactions (
  "Invoice" bigint not null,
  "InvoiceDate" timestamp with time zone null,
  "StockCode" text not null,
  "Quantity" bigint null,
  "Price" double precision null,
  "TotalPrice" double precision null,
  "Customer ID" bigint null,
  constraint transactions_pkey primary key ("Invoice", "StockCode")
) TABLESPACE pg_default;

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

create table public.items (
  "StockCode" text not null,
  "Description" text null,
  "Price" double precision null,
  constraint items_pkey primary key ("StockCode")
) TABLESPACE pg_default;

ALTER TABLE items ENABLE ROW LEVEL SECURITY;

create table public.rfm (
  "Customer ID" bigint not null,
  recency bigint null,
  frequency bigint null,
  monetary double precision null,
  "R" bigint null,
  "F" bigint null,
  "M" bigint null,
  "RFM_Score" bigint null,
  "Segment" text null,
  constraint rfm_pkey primary key ("Customer ID")
) TABLESPACE pg_default;

ALTER TABLE rfm ENABLE ROW LEVEL SECURITY;

create table public.marketing_campaigns (
  id uuid not null default gen_random_uuid (),
  name text not null,
  type text null,
  description text null,
  created_at timestamp without time zone null default now(),
  constraint marketing_campaigns_pkey primary key (id),
  constraint marketing_campaigns_type_check check (
    (
      type = any (
        array[
          'loyalty'::text,
          'referral'::text,
          're-engagement'::text
        ]
      )
    )
  )
) TABLESPACE pg_default;

ALTER TABLE marketing_campaigns ENABLE ROW LEVEL SECURITY;

create table public.campaign_emails (
  id uuid not null default gen_random_uuid (),
  campaign_id uuid null,
  customer_id bigint null,
  subject text null,
  body text null,
  sent_at timestamp without time zone null default now(),
  status text null default 'sent'::text,
  opened_at timestamp without time zone null,
  clicked_at timestamp without time zone null,
  constraint campaign_emails_pkey primary key (id),
  constraint campaign_emails_campaign_id_fkey foreign KEY (campaign_id) references marketing_campaigns (id) on update CASCADE on delete CASCADE,
  constraint campaign_emails_customer_id_fkey foreign KEY (customer_id) references customers ("Customer ID") on update CASCADE on delete CASCADE,
  constraint campaign_emails_status_check check (
    (
      status = any (
        array[
          'sent'::text,
          'bounced'::text,
          'opened'::text,
          'clicked'::text
        ]
      )
    )
  )
) TABLESPACE pg_default;

ALTER TABLE campaign_emails ENABLE ROW LEVEL SECURITY;
