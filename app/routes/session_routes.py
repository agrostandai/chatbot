from fastapi import APIRouter
from app.services.gemini_api import (
    get_user_session_info,
    clear_user_conversation,
    get_active_sessions_count,
    get_all_sessions_info
)

router = APIRouter()

@router.get("/session/{user_id}")
async def get_session_info(user_id: str):
    """Get session information for a specific user"""
    session_info = get_user_session_info(user_id)
    if session_info:
        return {
            "user_id": user_id,
            "session_info": session_info
        }
    else:
        return {
            "user_id": user_id,
            "session_info": None,
            "message": "No active session found"
        }

@router.delete("/session/{user_id}")
async def clear_session(user_id: str):
    """Clear a user's session"""
    success = clear_user_conversation(user_id)
    return {
        "user_id": user_id,
        "cleared": success,
        "message": "Session cleared" if success else "No active session to clear"
    }

@router.get("/sessions/stats")
async def get_sessions_stats():
    """Get statistics about all active sessions"""
    stats = get_all_sessions_info()
    return {
        "active_sessions": get_active_sessions_count(),
        "stats": stats
    }