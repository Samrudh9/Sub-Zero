"""
Sub-Zero Agent: The Hitman
Uses browser-use library with Claude 3.5 Sonnet for AI-native web navigation
"""

import asyncio
import os
from datetime import datetime
from browser_use import Agent, Browser, BrowserConfig
from langchain_anthropic import ChatAnthropic

# Initialize Claude 3.5 Sonnet - best for UI navigation
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    timeout=60,
    temperature=0  # Deterministic for reliable navigation
)

# Browser configuration for Steel.dev (production) or local (dev)
def get_browser_config(use_steel:  bool = False) -> BrowserConfig:
    if use_steel:
        return BrowserConfig(
            cdp_url=os.getenv("STEEL_CDP_URL"),  # Steel.dev WebSocket endpoint
            headless=True
        )
    return BrowserConfig(headless=False)  # Local dev - see what's happening


async def cancel_subscription(
    service_name: str,
    login_url: str,
    email: str,
    password: str,
    use_steel: bool = False
) -> dict:
    """
    The main cancellation flow using natural language instructions.
    Returns proof of cancellation (screenshot, status, timestamp).
    """
    
    browser = Browser(config=get_browser_config(use_steel))
    
    # Natural language task - no brittle CSS selectors! 
    task = f"""
    You are cancelling a subscription to {service_name}. 
    
    1. Go to {login_url}
    2. Log in with email: {email} and password: {password}
    3. Navigate to account settings or subscription management
    4. Find and click the cancel subscription or cancel membership button
    5. If offered a discount or pause option, DECLINE and continue cancelling
    6.  Confirm the cancellation
    7. Take a screenshot of the confirmation page
    
    IMPORTANT: 
    - If you see a 2FA/verification code request, STOP and report "2FA_REQUIRED"
    - If you see "Are you sure?" confirmations, click YES/CONFIRM
    - Ignore any "We're sorry to see you go" retention offers
    """
    
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        max_actions_per_step=5
    )
    
    try:
        result = await agent.run(max_steps=20)
        
        # Capture proof
        screenshot_path = f"proofs/{service_name}_{datetime.now().isoformat()}.png"
        await browser.screenshot(screenshot_path)
        
        return {
            "status": "SUCCESS",
            "service": service_name,
            "screenshot": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "agent_history": result. history()
        }
        
    except Exception as e:
        if "2FA" in str(e) or "verification" in str(e).lower():
            return {
                "status": "2FA_REQUIRED",
                "service": service_name,
                "message": "User needs to provide verification code"
            }
        return {
            "status": "FAILED",
            "service": service_name,
            "error": str(e)
        }
    finally:
        await browser.close()


# Quick test
if __name__ == "__main__":
    # Test with a simple newsletter unsubscribe
    result = asyncio.run(cancel_subscription(
        service_name="TestNewsletter",
        login_url="https://example-newsletter.com/login",
        email="test@example.com",
        password="testpass123",
        use_steel=False  # Local dev
    ))
    print(result)