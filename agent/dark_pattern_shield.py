"""
Dark Pattern Shield: Detects and defeats retention tricks
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

llm = ChatAnthropic(model="claude-sonnet-4-20250514")

DARK_PATTERNS = [
    "hidden_cancel_button",      # Button is grey, tiny, or requires scrolling
    "confirm_shaming",           # "No, I don't want to save money"
    "roach_motel",              # Easy to sign up, impossible to cancel
    "forced_continuity",        # Free trial → auto-charge without warning
    "misdirection",             # Bright "Keep Subscription" vs dim "Cancel"
    "obstruction",              # Multiple confirmation screens
    "retention_offer"           # "Stay for 50% off!" bait
]


async def analyze_page_for_dark_patterns(page_html: str, screenshot_base64: str) -> dict:
    """
    Uses Claude's vision to identify dark patterns on a cancellation page.
    Returns detected patterns and recommended actions.
    """
    
    prompt = f"""
    Analyze this subscription cancellation page for dark patterns. 
    
    Look for:
    1. Is the cancel button hidden, greyed out, or hard to find?
    2. Are there guilt-trip messages ("Are you SURE you want to leave?")
    3. Is there a bright "Keep Subscription" button next to a dim "Cancel"?
    4. Are there multiple unnecessary confirmation steps?
    5. Is there a retention offer (discount to stay)?
    
    Page HTML snippet: {page_html[: 2000]}
    
    Respond with:
    - detected_patterns: list of patterns found
    - cancel_button_selector: CSS selector or description of the REAL cancel button
    - recommended_action: what to click to actually cancel
    - confidence:  0-100
    """
    
    response = await llm.ainvoke([
        HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
        ])
    ])
    
    return response.content