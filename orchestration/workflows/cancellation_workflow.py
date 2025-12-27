"""
Temporal Workflow for subscription cancellation
Handles long-running operations, 2FA waits, and retries
"""

from datetime import timedelta
from temporalio import workflow
from temporalio. common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities.browser_activities import (
        start_cancellation,
        inject_2fa_code,
        capture_proof
    )
    from activities.notification_activities import send_push_notification


@workflow.defn
class CancellationWorkflow: 
    """
    Orchestrates the full cancellation flow with human-in-the-loop for 2FA
    """
    
    def __init__(self):
        self.two_fa_code:  str | None = None
        self.status = "PENDING"
    
    @workflow.signal
    async def provide_2fa_code(self, code: str):
        """Signal handler:  User provides 2FA code from their phone"""
        self.two_fa_code = code
    
    @workflow.query
    def get_status(self) -> str:
        return self.status
    
    @workflow.run
    async def run(self, request: dict) -> dict:
        """
        Main workflow execution
        
        request = {
            "user_id": "123",
            "service_name": "Netflix",
            "login_url":  "https://netflix.com/login",
            "encrypted_credentials": ".. .",  # Decrypted in Nitro Enclave
        }
        """
        self.status = "STARTING"
        
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(minutes=5),
            maximum_attempts=3
        )
        
        # Step 1: Start the cancellation attempt
        self.status = "NAVIGATING"
        result = await workflow.execute_activity(
            start_cancellation,
            request,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )
        
        # Step 2: Handle 2FA if required
        if result["status"] == "2FA_REQUIRED":
            self.status = "AWAITING_2FA"
            
            # Send push notification to user's phone
            await workflow.execute_activity(
                send_push_notification,
                {
                    "user_id":  request["user_id"],
                    "title": f"{request['service_name']} needs verification",
                    "body":  "Enter the code from your SMS/email to continue cancellation"
                },
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            # Wait for user to provide 2FA code (up to 10 minutes)
            try:
                await workflow.wait_condition(
                    lambda: self. two_fa_code is not None,
                    timeout=timedelta(minutes=10)
                )
            except TimeoutError:
                self.status = "TIMEOUT"
                return {"status": "FAILED", "reason": "2FA code not provided in time"}
            
            # Step 3: Inject 2FA and continue
            self.status = "VERIFYING_2FA"
            result = await workflow.execute_activity(
                inject_2fa_code,
                {
                    "session_id": result["session_id"],
                    "code": self.two_fa_code
                },
                start_to_close_timeout=timedelta(minutes=3)
            )
        
        # Step 4: Capture proof and finalize
        if result["status"] == "SUCCESS": 
            self.status = "CAPTURING_PROOF"
            proof = await workflow.execute_activity(
                capture_proof,
                {"session_id": result["session_id"]},
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            self.status = "COMPLETED"
            return {
                "status": "SUCCESS",
                "screenshot_url": proof["screenshot_url"],
                "video_url": proof. get("video_url"),  # From Steel.dev session recording
                "savings_per_year": request. get("annual_cost", 0),
                "cancelled_at": workflow.now().isoformat()
            }
        
        self.status = "FAILED"
        return result
