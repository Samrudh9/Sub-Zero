"""
Subscriptions API Router
Handles subscription detection, listing, and status updates
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

router = APIRouter()


# Pydantic Models
class Subscription(BaseModel):
    """Detected subscription from bank transactions"""
    id: str
    user_id: str
    merchant_name: str
    normalized_name: Optional[str] = None
    logo_url: Optional[str] = None
    monthly_price: float
    last_charge_date: Optional[date] = None
    status: str = "active"
    cancellation_url: Optional[str] = None


class SubscriptionStatusUpdate(BaseModel):
    """Update subscription status (e.g., mark as 'keeper')"""
    status: str = Field(..., pattern="^(active|cancelled|keeper|zombie)$")


class SyncRequest(BaseModel):
    """Request to sync transactions from Plaid"""
    user_id: str
    force_refresh: bool = False


# Dependencies
async def get_current_user() -> dict:
    """
    Get current authenticated user from Supabase JWT token.
    TODO: Implement actual JWT validation with Supabase.
    """
    # Placeholder - in production, validate JWT from Authorization header
    return {"user_id": "placeholder-user-id"}


@router.get("/subscriptions")
async def list_subscriptions(
    current_user: dict = Depends(get_current_user)
) -> List[Subscription]:
    """
    List all detected subscriptions for the authenticated user.
    
    Returns subscriptions sorted by monthly_price descending.
    """
    # TODO: Query Supabase subscriptions table
    # Example query:
    # supabase.table("subscriptions").select("*").eq("user_id", current_user["user_id"]).execute()
    
    return []  # Placeholder


@router.post("/subscriptions/sync")
async def sync_subscriptions(
    request: SyncRequest,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Trigger Plaid sync to fetch new transactions and detect subscriptions.
    
    This endpoint:
    1. Fetches recent transactions from Plaid
    2. Analyzes for recurring charges
    3. Updates subscriptions table with new detections
    
    Returns:
        dict: Status and count of new subscriptions detected
    """
    # Verify user owns this account
    if request.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # TODO: Implement Plaid transaction sync
    # 1. Get Plaid access token from bank_connections table
    # 2. Call plaid_client.get_transactions()
    # 3. Call plaid_client.detect_subscriptions()
    # 4. Upsert into subscriptions table
    
    return {
        "status": "success",
        "new_subscriptions_detected": 0,
        "message": "Sync completed (placeholder implementation)"
    }


@router.patch("/subscriptions/{subscription_id}/status")
async def update_subscription_status(
    subscription_id: str,
    update: SubscriptionStatusUpdate,
    current_user: dict = Depends(get_current_user)
) -> Subscription:
    """
    Update subscription status (e.g., mark as 'keeper' when user swipes right).
    
    Args:
        subscription_id: UUID of the subscription
        update: New status value
        
    Returns:
        Updated subscription object
    """
    # TODO: Update in Supabase
    # 1. Verify subscription belongs to current_user
    # 2. Update status field
    # 3. Return updated record
    
    raise HTTPException(status_code=501, detail="Not yet implemented")
