from fastapi import APIRouter
from app.config import settings
from app.services.gemini_api import get_active_sessions_count, get_all_sessions_info
import os

router = APIRouter()

# Environment variables with validation
TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN

@router.get("/debug/credentials")
async def debug_credentials():
    """Debug endpoint to check Twilio credentials (remove in production!)"""
    return {
        "twilio_account_sid": {
            "present": bool(TWILIO_ACCOUNT_SID),
            "format_valid": TWILIO_ACCOUNT_SID.startswith('AC') if TWILIO_ACCOUNT_SID else False,
            "preview": TWILIO_ACCOUNT_SID[:8] + "..." if TWILIO_ACCOUNT_SID else None,
            "length": len(TWILIO_ACCOUNT_SID) if TWILIO_ACCOUNT_SID else 0
        },
        "twilio_auth_token": {
            "present": bool(TWILIO_AUTH_TOKEN),
            "length": len(TWILIO_AUTH_TOKEN) if TWILIO_AUTH_TOKEN else 0
        },
        "env_check": {
            "from_env_sid": os.getenv("TWILIO_ACCOUNT_SID", "NOT_FOUND")[:8] + "..." if os.getenv("TWILIO_ACCOUNT_SID") else "NOT_FOUND",
            "from_env_token_length": len(os.getenv("TWILIO_AUTH_TOKEN") or "") if os.getenv("TWILIO_AUTH_TOKEN") else 0
        }
    }

@router.get("/debug/sessions")
async def debug_sessions():
    """Debug endpoint to check session manager status"""
    return {
        "session_manager_status": "active",
        "active_sessions": get_active_sessions_count(),
        "all_sessions": get_all_sessions_info()
    }