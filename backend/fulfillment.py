"""
Fulfillment trigger logic for food assistance requests
"""
import httpx
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

FULFILLMENT_WEBHOOK_URL = os.getenv("FULFILLMENT_WEBHOOK_URL", None)


async def trigger_fulfillment_notification(data: Dict[str, Any]) -> bool:
    """
    Trigger fulfillment process by sending notification to partners/NGOs.
    This can be extended to send to multiple endpoints, SMS, email, etc.
    """
    fulfillment_payload = {
        "person_name": data.get("person_name"),
        "age": data.get("age"),
        "location": data.get("location"),
        "food_request": data.get("food_requirement"),
        "assistance_type": data.get("assistance_type")
    }
    
    # If webhook URL is configured, send POST request
    if FULFILLMENT_WEBHOOK_URL:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    FULFILLMENT_WEBHOOK_URL,
                    json=fulfillment_payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                print(f"Fulfillment notification sent successfully: {fulfillment_payload}")
                return True
        except Exception as e:
            print(f"Error sending fulfillment notification: {e}")
            return False
    
    # Fallback: log the fulfillment request
    print(f"Fulfillment triggered (no webhook configured): {fulfillment_payload}")
    return True
