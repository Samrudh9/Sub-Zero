# Sub-Zero Temporal Activities

This directory contains Temporal activities used by the cancellation workflow orchestration layer.

## Overview

Activities are the building blocks of Temporal workflows that perform actual work, such as calling external services, interacting with databases, or executing business logic. Each activity is:

- **Async**: All activities are async functions for efficient I/O operations
- **Retryable**: Temporal automatically retries failed activities based on retry policies
- **Idempotent**: Activities should be designed to be safely retried
- **Logged**: All activities use structured logging for observability

## Activities

### Browser Activities (`browser_activities.py`)

Activities that interact with the browser automation layer to perform subscription cancellations.

#### `start_cancellation(request: dict) -> dict`

Initiates the browser-based cancellation flow by connecting to Steel.dev or local browser.

**Input:**
```python
{
    "user_id": "123",
    "service_name": "Netflix", 
    "login_url": "https://netflix.com/login",
    "email": "user@example.com",
    "password": "encrypted_password",
    "use_steel": False  # True for production with Steel.dev
}
```

**Output:**
```python
{
    "status": "SUCCESS" | "2FA_REQUIRED" | "FAILED",
    "session_id": "session_uuid",
    "message": "Optional status message",
    "screenshot_path": "path/to/screenshot.png"
}
```

#### `inject_2fa_code(request: dict) -> dict`

Injects a 2FA verification code into an existing browser session.

**Input:**
```python
{
    "session_id": "session_uuid",
    "code": "123456"
}
```

**Output:**
```python
{
    "status": "SUCCESS" | "FAILED",
    "session_id": "session_uuid",
    "message": "Optional status message"
}
```

#### `capture_proof(request: dict) -> dict`

Captures screenshot/video proof of successful cancellation.

**Input:**
```python
{
    "session_id": "session_uuid"
}
```

**Output:**
```python
{
    "screenshot_url": "https://storage.supabase.co/...",
    "video_url": "https://steel.dev/sessions/.../recording.mp4",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Notification Activities (`notification_activities.py`)

Activities for sending push notifications to users.

#### `send_push_notification(request: dict) -> dict`

Sends a push notification to user's mobile device via FCM/APNs.

**Input:**
```python
{
    "user_id": "123",
    "title": "Netflix needs verification",
    "body": "Enter the code from your SMS/email",
    "data": {}  # Optional additional payload
}
```

**Output:**
```python
{
    "status": "SUCCESS" | "FAILED",
    "delivery_status": "Notification sent to all devices",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## Usage in Workflows

Activities are imported and executed within workflows using the Temporal API:

```python
from temporalio import workflow
from activities.browser_activities import start_cancellation

@workflow.defn
class CancellationWorkflow:
    @workflow.run
    async def run(self, request: dict) -> dict:
        result = await workflow.execute_activity(
            start_cancellation,
            request,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_attempts=3
            )
        )
        return result
```

## Development Notes

### Current Implementation Status

- ✅ **Activity Definitions**: All activities are defined with proper decorators
- ✅ **Browser Integration**: `start_cancellation` integrates with `agent/browser_agent.py`
- ⚠️ **2FA Injection**: Placeholder implementation (requires session management)
- ⚠️ **Proof Capture**: Placeholder implementation (requires Supabase integration)
- ⚠️ **Push Notifications**: Placeholder implementation (requires FCM/APNs setup)

### TODO

1. **2FA Session Management**
   - Implement browser session persistence/reconnection
   - Add support for resuming browser sessions by session_id
   
2. **Storage Integration**
   - Integrate with Supabase storage for screenshot uploads
   - Add video proof storage from Steel.dev sessions
   
3. **Notification Integration**
   - Set up FCM for Android push notifications
   - Set up APNs for iOS push notifications
   - Implement device token management

4. **Error Handling**
   - Add more granular error types
   - Implement circuit breakers for external services
   - Add better retry strategies for specific failure types

## Testing

Run the structural verification script to validate the activities setup:

```bash
cd /home/runner/work/Sub-Zero/Sub-Zero
python orchestration/verify_structure.py
```

This verifies:
- File structure is correct
- Python syntax is valid
- All required functions are defined
- Exports are properly configured

## Dependencies

Activities depend on:
- `temporalio` - Temporal SDK for Python
- `structlog` - Structured logging
- `agent/browser_agent.py` - Browser automation logic
- External services (to be integrated):
  - Steel.dev - Browser anti-bot evasion
  - Supabase - Storage for proof screenshots/videos
  - FCM/APNs - Push notification delivery
