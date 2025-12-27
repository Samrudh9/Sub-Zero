"""
Cancellations API Router
Handles subscription cancellation workflows and graveyard management
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

router = APIRouter()


# Pydantic Models
class CancellationRequest(BaseModel):
    """Request to start a new cancellation workflow"""
    subscription_id: str
    user_id: str
    service_name: str
    login_url: str
    encrypted_credentials: Optional[str] = None


class CancellationStatus(BaseModel):
    """Status of an ongoing cancellation"""
    id: str
    status: str = Field(
        ...,
        description="Current status: PENDING, STARTING, NAVIGATING, AWAITING_2FA, VERIFYING_2FA, CAPTURING_PROOF, COMPLETED, FAILED"
    )
    service_name: str
    started_at: datetime
    requires_2fa: bool = False
    proof_screenshot_url: Optional[str] = None


class TwoFactorCode(BaseModel):
    """2FA code submission for pending cancellation"""
    code: str = Field(..., min_length=4, max_length=8)


class GraveyardEntry(BaseModel):
    """Entry in the graveyard of cancelled subscriptions"""
    id: str
    service_name: str
    monthly_savings: Decimal
    cancelled_at: datetime
    proof_screenshot_url: Optional[str] = None
    proof_video_url: Optional[str] = None
    cancellation_method: str


class TotalSavings(BaseModel):
    """Total annual savings from cancelled subscriptions"""
    total_annual_savings: Decimal
    cancelled_count: int


# Dependencies
async def get_current_user() -> dict:
    """
    Get current authenticated user from Supabase JWT token.
    TODO: Implement actual JWT validation with Supabase.
    """
    return {"user_id": "placeholder-user-id"}


@router.post("/cancellations")
async def start_cancellation(
    request: CancellationRequest,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Start a new cancellation workflow using Temporal.
    
    This endpoint:
    1. Validates user owns the subscription
    2. Retrieves encrypted credentials from vault
    3. Starts Temporal workflow for agent execution
    4. Returns workflow ID for status tracking
    
    Returns:
        dict: Workflow ID and initial status
    """
    # Verify user owns this subscription
    if request.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # TODO: Implement workflow start
    # 1. Get encrypted credentials from credential_vault table
    # 2. Start Temporal CancellationWorkflow
    # 3. Return workflow_id for tracking
    
    return {
        "workflow_id": "placeholder-workflow-id",
        "status": "PENDING",
        "message": "Cancellation workflow started (placeholder)"
    }


@router.get("/cancellations/{workflow_id}/status")
async def get_cancellation_status(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
) -> CancellationStatus:
    """
    Check the status of an ongoing cancellation workflow.
    
    Queries Temporal workflow status and returns current state.
    Mobile app can poll this endpoint to show progress.
    
    Returns:
        CancellationStatus with current workflow state
    """
    # TODO: Query Temporal workflow status
    # temporal_client.get_workflow_handle(workflow_id).query("get_status")
    
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/cancellations/{workflow_id}/2fa")
async def submit_2fa_code(
    workflow_id: str,
    code: TwoFactorCode,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Submit 2FA code for a pending cancellation workflow.
    
    This sends a signal to the Temporal workflow to inject the 2FA code
    and continue the cancellation process.
    
    Args:
        workflow_id: The Temporal workflow ID
        code: The 2FA code from user's SMS/email
        
    Returns:
        dict: Confirmation that code was submitted
    """
    # TODO: Send signal to Temporal workflow
    # temporal_client.get_workflow_handle(workflow_id).signal("provide_2fa_code", code.code)
    
    return {
        "status": "success",
        "message": "2FA code submitted (placeholder)"
    }


@router.get("/graveyard")
async def get_graveyard(
    current_user: dict = Depends(get_current_user)
) -> List[GraveyardEntry]:
    """
    Get all cancelled subscriptions for the user (The Graveyard).
    
    Shows history of successful cancellations with proof and savings.
    
    Returns:
        List of graveyard entries sorted by cancelled_at descending
    """
    # TODO: Query Supabase graveyard table
    # supabase.table("graveyard").select("*").eq("user_id", current_user["user_id"]).order("cancelled_at", desc=True).execute()
    
    return []  # Placeholder


@router.get("/graveyard/savings")
async def get_total_savings(
    current_user: dict = Depends(get_current_user)
) -> TotalSavings:
    """
    Calculate total annual savings from all cancelled subscriptions.
    
    Uses the get_total_savings() PostgreSQL function.
    
    Returns:
        Total annual savings amount and count of cancelled subscriptions
    """
    # TODO: Call PostgreSQL function
    # result = supabase.rpc("get_total_savings", {"p_user_id": current_user["user_id"]}).execute()
    
    return TotalSavings(
        total_annual_savings=Decimal("0.00"),
        cancelled_count=0
    )
