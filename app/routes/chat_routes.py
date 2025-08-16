from fastapi import APIRouter, HTTPException
from app.services.mongo_db import save_user, save_message
from app.services.gemini_api import (
    chat_with_gpt, 
    extract_crop_type_from_ai_response,
    get_user_session_info
)
from app.models import TextChatRequest

router = APIRouter()

@router.post("/chat")
async def handle_text_chat(req: TextChatRequest):
    """Enhanced text chat with session management and proper message saving"""
    try:
        # Validate input
        if not req.user_id or not req.message:
            raise HTTPException(status_code=400, detail="user_id and message are required")

        # Save user (only once, prevents duplicates)
        save_user(req.user_id, "", req.user_name or "")

        # Get AI response with crop type (this now includes session management)
        reply, crop_type = await chat_with_gpt(req.message, req.user_id)

        # Save user message to database
        user_crop_type = extract_crop_type_from_ai_response(req.message) if not crop_type else crop_type
        save_message(
            user_id=req.user_id,
            message=req.message,
            is_bot=False,
            crop_type=user_crop_type
        )

        # Save bot reply to database
        save_message(
            user_id=req.user_id,
            message=reply,
            is_bot=True,
            crop_type=crop_type
        )

        # Get session info
        session_info = get_user_session_info(req.user_id)

        return {
            "user_id": req.user_id,
            "reply": reply,
            "crop_type": crop_type if crop_type else "Not identified",
            "session_info": {
                "message_count": session_info.get("message_count", 0) if session_info else 0,
                "time_remaining": session_info.get("time_remaining", 0) if session_info else 0
            }
        }

    except Exception as e:
        error_reply = f"⚠️ Kuch problem hui hai. Phir se try kariye. (Error: {str(e)})"
        # Save error message too
        save_message(
            user_id=req.user_id,
            message=error_reply,
            is_bot=True,
            crop_type=""
        )
        return {
            "user_id": req.user_id,
            "reply": error_reply,
            "error": True
        }