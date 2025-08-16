from fastapi import APIRouter, HTTPException
from app.services.mongo_db import save_user, save_message
from app.services.gemini_api import analyze_crop_image, get_user_session_info
from app.models import ImageRequest

router = APIRouter()

@router.post("/upload-image")
async def handle_image_upload(payload: ImageRequest):
    """Enhanced image analysis with session management and proper message saving"""
    try:
        # Validate input
        if not payload.user_id or not payload.base64_image:
            raise HTTPException(status_code=400, detail="user_id and base64_image are required")

        # Save user (only once)
        save_user(payload.user_id, "", payload.user_name or "")

        # Enhanced image analysis with session management
        diagnosis, crop_type = await analyze_crop_image(
            payload.base64_image, 
            payload.user_id  # Now includes session management
        )

        # Save image upload to database (store base64 instead of message)
        save_message(
            user_id=payload.user_id,
            message="",  # Empty message for image
            image_base64=payload.base64_image,
            is_bot=False,
            crop_type=crop_type
        )

        # Save diagnosis to database
        save_message(
            user_id=payload.user_id,
            message=diagnosis,
            is_bot=True,
            crop_type=crop_type
        )

        # Get session info
        session_info = get_user_session_info(payload.user_id)

        return {
            "user_id": payload.user_id,
            "diagnosis": diagnosis,
            "crop_type": crop_type if crop_type else "Not identified",
            "session_info": {
                "message_count": session_info.get("message_count", 0) if session_info else 0,
                "time_remaining": session_info.get("time_remaining", 0) if session_info else 0
            }
        }

    except Exception as e:
        error_msg = f"⚠️ Image analysis mein problem: {str(e)}"
        save_message(
            user_id=payload.user_id,
            message=error_msg,
            is_bot=True,
            crop_type=""
        )
        return {
            "user_id": payload.user_id,
            "diagnosis": error_msg,
            "error": True
        }