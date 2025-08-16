from fastapi import APIRouter, Request
from app.services.mongo_db import save_user, save_message
from app.services.gemini_api import chat_with_gpt, analyze_crop_image, get_user_session_info
from app.services.whatsapp_api import send_whatsapp_message
from app.utils.helper import extract_phone_number, format_whatsapp_message, download_twilio_media
import base64

router = APIRouter()

@router.post("/webhook")
async def webhook(req: Request):
    """Enhanced WhatsApp webhook with session management and proper message saving"""
    try:
        # Parse form data
        form = await req.form()
        
        # Extract information
        body_field = form.get("Body", "")
        if isinstance(body_field, str):
            message = body_field.strip()
        else:
            message = ""
        from_field = form.get("From", "")
        if not isinstance(from_field, str):
            from_field = str(from_field)
        phone_number = extract_phone_number(from_field)
        media_url = form.get("MediaUrl0")
        
        if not phone_number:
            return {"status": "error", "message": "No phone number provided"}

        # Use phone number as user_id for WhatsApp users
        user_id = phone_number
        
        # ---------------- TEXT MESSAGE HANDLING WITH SESSION MANAGEMENT ----------------
        if message and not media_url:
            # Save user with phone number
            save_user(user_id, phone_number, "")

            # Get AI response with crop type (includes session management)
            reply, crop_type = await chat_with_gpt(message, user_id)

            # Save user message to database
            save_message(
                user_id=user_id,
                message=message,
                is_bot=False,
                crop_type=crop_type
            )

            # Format and send response in properly sized chunks
            message_chunks = format_whatsapp_message(reply, max_length=1500)
            
            for i, chunk in enumerate(message_chunks):
                # Save each bot reply chunk to database
                save_message(
                    user_id=user_id,
                    message=chunk,
                    is_bot=True,
                    crop_type=crop_type
                )
                
                # Add message number indicator for multi-part messages
                if len(message_chunks) > 1:
                    chunk_indicator = f"({i+1}/{len(message_chunks)})\n{chunk}"
                else:
                    chunk_indicator = chunk
                    
                send_whatsapp_message(phone_number, chunk_indicator)

            # Send session info to user if it's a long conversation
            session_info = get_user_session_info(user_id)
            if session_info and session_info.get("message_count", 0) > 20:
                session_msg = f"💬 Session: {session_info.get('message_count', 0)} messages, {session_info.get('time_remaining', 0)//60:.0f} min remaining"
                send_whatsapp_message(phone_number, session_msg)

        # ---------------- IMAGE MESSAGE HANDLING WITH SESSION MANAGEMENT ----------------
        elif media_url:
            try:
                # Save user with phone number
                save_user(user_id, phone_number, "")

                # Send acknowledgment
                ack_message = "📸 Photo mil gayi! Analysis ho raha hai...\n(Image received! Analyzing...)"
                send_whatsapp_message(phone_number, ack_message)
                
                # Save acknowledgment message to database
                save_message(
                    user_id=user_id,
                    message=ack_message,
                    is_bot=True,
                    crop_type=""
                )

                # Download image with improved authentication
                try:
                    if not isinstance(media_url, str):
                        media_url_str = str(media_url)
                    else:
                        media_url_str = media_url
                    image_content = download_twilio_media(media_url_str)
                    print(f"Successfully downloaded image for {phone_number}, size: {len(image_content)} bytes")
                except Exception as download_error:
                    print(f"Image download error for {phone_number}: {str(download_error)}")
                    raise download_error

                # Convert to base64
                image_base64 = base64.b64encode(image_content).decode('utf-8')
                print(f"Image converted to base64 for {phone_number}, length: {len(image_base64)}")

                # Analyze image with context and session management
                diagnosis, crop_type = await analyze_crop_image(image_base64, user_id)
                
                # Save image upload to database (store base64 instead of message text)
                save_message(
                    user_id=user_id,
                    message="",  # Empty message for image uploads
                    image_base64=image_base64,
                    is_bot=False,
                    crop_type=crop_type
                )
                
                # Format and send diagnosis in proper chunks
                diagnosis_chunks = format_whatsapp_message(diagnosis, max_length=1500)
                
                for i, chunk in enumerate(diagnosis_chunks):
                    # Save each diagnosis chunk to database
                    save_message(
                        user_id=user_id,
                        message=chunk,
                        is_bot=True,
                        crop_type=crop_type
                    )
                    
                    if len(diagnosis_chunks) > 1:
                        chunk_with_indicator = f"📋 Report ({i+1}/{len(diagnosis_chunks)})\n{chunk}"
                    else:
                        chunk_with_indicator = f"📋 Fasal Analysis Report:\n{chunk}"
                        
                    send_whatsapp_message(phone_number, chunk_with_indicator)

                # Send follow-up options
                follow_up_msg = (
                    "\n💬 Aur jaankari ke liye puchiye:\n"
                    "• 'treatment' - detailed ilaj\n"
                    "• 'prevention' - future bachav\n"
                    "• 'medicine' - dawa ki jaankari\n\n"
                    "Ask for more info:\n"
                    "• 'उपचार' or 'treatment'\n"
                    "• 'रोकथाम' or 'prevention'\n"
                    "• 'दवा' or 'medicine'"
                )
                send_whatsapp_message(phone_number, follow_up_msg)
                
                # Save follow-up message to database
                save_message(
                    user_id=user_id,
                    message=follow_up_msg,
                    is_bot=True,
                    crop_type=crop_type
                )

            except Exception as e:
                error_msg = f"❌ Photo processing mein problem: {str(e)[:100]}..."
                print(f"Image processing error for {phone_number}: {str(e)}")
                send_whatsapp_message(phone_number, error_msg)
                
                # Save error message to database
                save_message(
                    user_id=user_id,
                    message=error_msg,
                    is_bot=True,
                    crop_type=""
                )

        # If neither text nor image
        else:
            help_msg = (
                "🌾 *Krishi Sahayak Bot*\n\n"
                "Main aapki fasal ki problem mein madad kar sakta hun:\n"
                "📸 Fasal ki photo bhejiye\n"
                "💬 Apni problem likhiye\n"
                "📍 Apna location bataiye\n\n"
                "*Agri Help Bot*\n"
                "I can help with crop problems:\n"
                "📸 Send crop photos\n"
                "💬 Describe your problem\n"
                "📍 Share your location"
            )
            send_whatsapp_message(phone_number, help_msg)
            
            # Save help message to database
            save_user(user_id, phone_number, "")
            save_message(
                user_id=user_id,
                message=help_msg,
                is_bot=True,
                crop_type=""
            )

        return {"status": "success"}

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}