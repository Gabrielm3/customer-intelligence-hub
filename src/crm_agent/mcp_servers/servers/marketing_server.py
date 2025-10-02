from mcp.server.fastmcp import FastMCP
from sqlalchemy import text
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(url=os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MCP Server

mcp = FastMCP("marketing")


@mcp.tool()
async def create_campaign(
    name: str,
    type: str,
    description: str,
) -> int:
    """Create a marketing campaign.
    
    Args:
        name: The name of the campaign.
        type: The type of the campaign. One of: loyalty, referral, re-engagement
        description: The description of the campaign.

    Returns:
        The ID of the created campaign.
    """
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                INSERT INTO marketing_campaigns (name, type, description)
                VALUES (:name, :type, :description)
                RETURNING id
                """
            ),
            {"name": name, "type": type, "description": description},
        )
        session.commit()
        return result.fetchone()[0]

@mcp.tool()
async def send_campaign_email(
    campaign_id: int | str,
    customer_id: int,
    subject: str,
    body: str,
) -> str:
    """Send a campaign email.
    
    Args:
        campaign_id: The ID of the campaign (integer or string representation).
        customer_id: The ID of the customer.
        subject: The subject of the email.
        body: The body of the email.

    Returns:
        A confirmation that the email was sent.
    """
    
    try:
        campaign_id_int = int(campaign_id)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid campaign_id: {campaign_id}. Must be an integer or string representation of an integer.")
   
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                INSERT INTO campaign_emails (campaign_id, customer_id, email_subject, email_body)
                VALUES (:campaign_id, :customer_id, :subject, :body)
                """
            ),
            {"campaign_id": campaign_id_int, "customer_id": customer_id, "subject": subject, "body": body},
        )
        session.commit()

    return f"Successfully sent <{subject}> to customer <{customer_id}>!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
