from fastapi import APIRouter
from app.services.mongo_db import save_message
from app.services.gemini_api import get_treatment_followup, get_user_session_info
from app.models import TreatmentRequest

router = APIRouter()

@router.post("/treatment-details")
async def get_treatment_details(req: TreatmentRequest):
    """Get detailed treatment information with session context"""
    try:
        # Get detailed treatment guidance with session context
        treatment_details = get_treatment_followup(req.disease, req.crop, req.user_id)
        
        # Save interaction to database
        save_message(
            user_id=req.user_id,
            message=f"Treatment request: {req.disease} in {req.crop}",
            is_bot=False,
            crop_type=req.crop
        )
        save_message(
            user_id=req.user_id,
            message=treatment_details,
            is_bot=True,
            crop_type=req.crop
        )
        
        # Get session info
        session_info = get_user_session_info(req.user_id)
        
        return {
            "user_id": req.user_id,
            "disease": req.disease,
            "crop": req.crop,
            "treatment_details": treatment_details,
            "session_info": {
                "message_count": session_info.get("message_count", 0) if session_info else 0,
                "time_remaining": session_info.get("time_remaining", 0) if session_info else 0
            }
        }
        
    except Exception as e:
        error_msg = f"Treatment info mein problem: {str(e)}"
        save_message(
            user_id=req.user_id,
            message=error_msg,
            is_bot=True,
            crop_type=req.crop
        )
        return {
            "user_id": req.user_id,
            "error": error_msg
        }