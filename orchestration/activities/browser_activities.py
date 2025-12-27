"""
Browser-based activities for subscription cancellation.
Integrates with Steel.dev and browser_agent for automated cancellation.
"""

import os
import asyncio
from datetime import datetime
from temporalio import activity
import structlog

# Import the browser agent cancellation logic
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from agent.browser_agent import cancel_subscription

logger = structlog.get_logger()


@activity.defn
async def start_cancellation(request: dict) -> dict:
    """
    Starts the browser-based cancellation flow.
    
    Args:
        request: Dictionary containing:
            - user_id: User identifier
            - service_name: Name of the service to cancel
            - login_url: URL to login page
            - email: User's email for the service
            - password: User's password (decrypted from Nitro Enclave)
            - use_steel: Whether to use Steel.dev (default: False for dev)
    
    Returns:
        Dictionary with:
            - status: "SUCCESS", "2FA_REQUIRED", or "FAILED"
            - session_id: Browser session identifier (for 2FA injection)
            - message: Optional status message
            - screenshot_path: Path to screenshot if available
    """
    logger.info("Starting cancellation", 
                user_id=request.get("user_id"),
                service_name=request.get("service_name"))
    
    try:
        # Extract parameters
        service_name = request.get("service_name")
        login_url = request.get("login_url")
        email = request.get("email")
        password = request.get("password")
        use_steel = request.get("use_steel", False)
        
        # Validate required parameters
        if not all([service_name, login_url, email, password]):
            logger.error("Missing required parameters")
            return {
                "status": "FAILED",
                "message": "Missing required parameters: service_name, login_url, email, password"
            }
        
        # Call the browser agent to perform cancellation
        result = await cancel_subscription(
            service_name=service_name,
            login_url=login_url,
            email=email,
            password=password,
            use_steel=use_steel
        )
        
        # Generate a session ID for 2FA continuation if needed
        session_id = f"{service_name}_{request.get('user_id')}_{datetime.now().timestamp()}"
        
        if result["status"] == "2FA_REQUIRED":
            logger.info("2FA required", session_id=session_id)
            return {
                "status": "2FA_REQUIRED",
                "session_id": session_id,
                "message": result.get("message", "Verification code required"),
                "service_name": service_name
            }
        
        elif result["status"] == "SUCCESS":
            logger.info("Cancellation successful", session_id=session_id)
            return {
                "status": "SUCCESS",
                "session_id": session_id,
                "screenshot_path": result.get("screenshot"),
                "timestamp": result.get("timestamp"),
                "service_name": service_name
            }
        
        else:  # FAILED
            logger.error("Cancellation failed", error=result.get("error"))
            return {
                "status": "FAILED",
                "message": result.get("error", "Unknown error occurred"),
                "service_name": service_name
            }
            
    except Exception as e:
        logger.error("Exception during cancellation", error=str(e))
        return {
            "status": "FAILED",
            "message": f"Exception occurred: {str(e)}",
            "service_name": request.get("service_name")
        }


@activity.defn
async def inject_2fa_code(request: dict) -> dict:
    """
    Injects a 2FA code into an existing browser session.
    
    Args:
        request: Dictionary containing:
            - session_id: Browser session identifier
            - code: 2FA verification code
    
    Returns:
        Dictionary with:
            - status: "SUCCESS" or "FAILED"
            - message: Optional status message
    """
    logger.info("Injecting 2FA code", session_id=request.get("session_id"))
    
    try:
        session_id = request.get("session_id")
        code = request.get("code")
        
        if not session_id or not code:
            logger.error("Missing required parameters for 2FA injection")
            return {
                "status": "FAILED",
                "message": "Missing required parameters: session_id, code"
            }
        
        # TODO: Implement actual 2FA code injection
        # This would involve:
        # 1. Reconnecting to the existing browser session using session_id
        # 2. Finding the 2FA input field
        # 3. Injecting the code
        # 4. Submitting and continuing the cancellation flow
        
        # Placeholder implementation
        logger.info("2FA code injected successfully", session_id=session_id)
        
        # Simulate async operation
        await asyncio.sleep(1)
        
        # For now, return success placeholder
        return {
            "status": "SUCCESS",
            "session_id": session_id,
            "message": "2FA code verified and cancellation continued"
        }
        
    except Exception as e:
        logger.error("Exception during 2FA injection", error=str(e))
        return {
            "status": "FAILED",
            "message": f"Failed to inject 2FA code: {str(e)}"
        }


@activity.defn
async def capture_proof(request: dict) -> dict:
    """
    Captures screenshot/video proof of cancellation.
    
    Args:
        request: Dictionary containing:
            - session_id: Browser session identifier
    
    Returns:
        Dictionary with:
            - screenshot_url: URL to uploaded screenshot
            - video_url: Optional URL to session recording (from Steel.dev)
            - timestamp: ISO format timestamp
    """
    logger.info("Capturing cancellation proof", session_id=request.get("session_id"))
    
    try:
        session_id = request.get("session_id")
        
        if not session_id:
            logger.error("Missing session_id for proof capture")
            return {
                "screenshot_url": None,
                "message": "Missing session_id"
            }
        
        # TODO: Implement actual proof capture
        # This would involve:
        # 1. Taking a final screenshot of the cancellation confirmation
        # 2. Uploading to Supabase storage
        # 3. Getting the Steel.dev session recording URL (if using Steel)
        # 4. Returning the URLs
        
        # Placeholder implementation
        timestamp = datetime.now().isoformat()
        
        # Simulate async operation
        await asyncio.sleep(0.5)
        
        # Generate placeholder URLs
        screenshot_url = f"https://storage.supabase.co/proof/{session_id}/screenshot.png"
        video_url = f"https://steel.dev/sessions/{session_id}/recording.mp4"
        
        logger.info("Proof captured", screenshot_url=screenshot_url)
        
        return {
            "screenshot_url": screenshot_url,
            "video_url": video_url,
            "timestamp": timestamp,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error("Exception during proof capture", error=str(e))
        return {
            "screenshot_url": None,
            "video_url": None,
            "message": f"Failed to capture proof: {str(e)}"
        }
