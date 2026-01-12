from fastapi import APIRouter
from schemas import ChatRequest, ChatResponse
from supabase_client import supabase
from fulfillment import trigger_fulfillment_notification
import uuid
import re
from datetime import datetime
from typing import Dict

router = APIRouter()

# In-memory session store (in production, use Redis or database)
sessions: Dict[str, Dict] = {}

def extract_name(text: str) -> str | None:
    """Extract name from user text"""
    name_patterns = [
        r"(?:i'?m|i am|my name is|name is|called|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            potential_name = match.group(1).strip()
            if len(potential_name.split()) <= 3:
                return potential_name
    if len(text.split()) <= 3 and text.replace(" ", "").isalpha():
        return text.strip()
    return None

def extract_age(text: str) -> int | None:
    """Extract age from user text"""
    age_patterns = [
        r"(?:i am|age is|i'?m|years old|year old)\s+(\d{1,3})",
        r"\b(\d{1,3})\s*(?:years?|yrs?|old)?\b",
        r"^(\d{1,3})$"
    ]
    for pattern in age_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            potential_age = int(match.group(1))
            if 1 <= potential_age <= 120:
                return potential_age
    return None

async def store_in_supabase(session_data: Dict, session_id: str) -> bool:
    """Store food assistance request in Supabase"""
    if not supabase:
        print("⚠️ Supabase not configured. Skipping database storage.")
        print("   Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return False
    
    # Validate required fields
    person_name = session_data.get("person_name")
    age = session_data.get("age")
    location = session_data.get("location")
    food_requirement = session_data.get("food_requirement", "General food assistance")
    
    if not person_name or not age or not location:
        print(f"❌ Missing required fields. Name: {person_name}, Age: {age}, Location: {location}")
        return False
    
    try:
        supabase_data = {
            "person_name": person_name,
            "age": age,
            "location": location,
            "food_request": food_requirement,
            "assistance_type": session_data.get("assistance_type", "immediate"),
            "session_id": session_id,
            "status": "pending"
        }
        
        print(f"📤 Attempting to store data in Supabase: {supabase_data}")
        
        result = supabase.table("food_assistance_requests").insert(supabase_data).execute()
        
        if result.data:
            print(f"✅ Data stored in Supabase successfully!")
            print(f"   Record ID: {result.data[0].get('id', 'N/A')}")
            print(f"   Person: {person_name}, Age: {age}, Location: {location}")
            return True
        else:
            print(f"⚠️ Supabase insert returned no data")
            return False
            
    except Exception as e:
        print(f"❌ Error storing data in Supabase: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest):
    """
    Chat endpoint with session-based state tracking and Supabase storage
    """
    user_msg_original = (chat_request.message or "").strip()
    user_msg = user_msg_original.lower().strip()
    
    # Get or create session_id
    session_id = chat_request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        # Initialize session if it doesn't exist
        is_new_session = session_id not in sessions
        
        if is_new_session:
            sessions[session_id] = {
                "step": "start",
                "person_name": None,
                "age": None,
                "location": None,
                "food_requirement": None,
                "assistance_type": "immediate"
            }
            # Only send greeting if user sent an empty message (initialization)
            if not user_msg_original or user_msg_original == "":
                return ChatResponse(
                    reply="Hello! I'm your AI food assistance helper. I'm here to help you get free food within 10 minutes. How can I assist you today?",
                    session_id=session_id
                )
            # If user sent a message on first request, continue processing below
        
        session = sessions[session_id]
        
        # Ensure session has required keys
        if "step" not in session:
            session["step"] = "start"
        if "person_name" not in session:
            session["person_name"] = None
        if "age" not in session:
            session["age"] = None
        if "location" not in session:
            session["location"] = None
        
        # Debug logging
        print(f"🔍 Session: {session_id[:8]}..., Step: {session['step']}, Message: '{user_msg_original[:50]}'")
        print(f"   Current session state: name={session.get('person_name')}, age={session.get('age')}, location={session.get('location')}")
        
        # Process based on current step
        if session["step"] == "start":
            # If user sent any non-empty message, proceed to ask for name
            # This prevents the loop of asking "please let me know if you need food"
            if user_msg_original and len(user_msg_original.strip()) > 0:
                session["step"] = "asking_name"  # CRITICAL: Advance step to prevent loop
                print(f"✅ Step advanced: start → asking_name")
                return ChatResponse(
                    reply="Hello! I'm here to help you get food assistance. To proceed, I need a few details. Could you please tell me your name?",
                    session_id=session_id
                )
            else:
                # Only ask again if message is truly empty
                return ChatResponse(
                    reply="I'm here to help with food assistance. Please let me know if you need food.",
                    session_id=session_id
                )
        
        elif session["step"] == "asking_name":
            # CRITICAL: Accept ANY input (even empty) to prevent infinite loops
            # If we're in asking_name step, any message should be treated as a name
            if user_msg_original and len(user_msg_original.strip()) > 0:
                name = extract_name(user_msg_original)
                if name:
                    session["person_name"] = name
                else:
                    # Accept the input as-is if extraction fails
                    session["person_name"] = user_msg_original.strip()
            else:
                # Even if empty, assign a default to prevent loop
                session["person_name"] = "User"
            
            # ALWAYS advance step - this is critical to prevent loops
            session["step"] = "asking_age"
            print(f"✅ Step advanced: asking_name → asking_age, Name: {session['person_name']}")
            return ChatResponse(
                reply=f"Thank you, {session['person_name']}! Could you please tell me your age?",
                session_id=session_id
            )
        
        elif session["step"] == "asking_age":
            age = extract_age(user_msg)
            if age is not None:
                session["age"] = age
                session["step"] = "asking_location"
                print(f"✅ Step advanced: asking_age → asking_location, Age: {age}")
                return ChatResponse(
                    reply="Thank you! Could you please tell me your location or area where you need the food delivered?",
                    session_id=session_id
                )
            else:
                # Try to extract number from message
                numbers = re.findall(r'\d+', user_msg)
                if numbers:
                    potential_age = int(numbers[0])
                    if 1 <= potential_age <= 120:
                        session["age"] = potential_age
                        session["step"] = "asking_location"
                        print(f"✅ Step advanced: asking_age → asking_location, Age: {potential_age}")
                        return ChatResponse(
                            reply="Thank you! Could you please tell me your location or area where you need the food delivered?",
                            session_id=session_id
                        )
                
                # Track attempts to prevent infinite loop
                if "_age_attempts" not in session:
                    session["_age_attempts"] = 0
                session["_age_attempts"] += 1
                
                # After 2 attempts, accept any number or default and move on
                if session["_age_attempts"] >= 2:
                    # Try to get any number from the message
                    if numbers:
                        session["age"] = int(numbers[0]) if 1 <= int(numbers[0]) <= 120 else 25
                    else:
                        session["age"] = 25  # Default age
                    session["step"] = "asking_location"
                    print(f"⚠️ Age attempts exceeded ({session['_age_attempts']}), using age {session['age']}, advancing to location")
                    return ChatResponse(
                        reply="Thank you! Could you please tell me your location or area where you need the food delivered?",
                        session_id=session_id
                    )
                
                return ChatResponse(
                    reply="I need to know your age. Could you please tell me how old you are? (e.g., 25)",
                    session_id=session_id
                )
        
        elif session["step"] == "asking_location":
            # Accept any input as location to prevent loops
            if user_msg_original and len(user_msg_original.strip()) > 0:
                session["location"] = user_msg_original.strip()
                session["step"] = "asking_food_requirement"
                print(f"✅ Step advanced: asking_location → asking_food_requirement, Location: {session['location']}")
                return ChatResponse(
                    reply="Great! Could you please tell me what kind of food you need or any specific requirements?",
                    session_id=session_id
                )
            else:
                # Even if empty, use a default and advance to prevent loop
                session["location"] = "Not specified"
                session["step"] = "asking_food_requirement"
                print(f"⚠️ Empty location, using default, advancing to food_requirement")
                return ChatResponse(
                    reply="Great! Could you please tell me what kind of food you need or any specific requirements?",
                    session_id=session_id
                )
        
        elif session["step"] == "asking_food_requirement":
            # Accept any response as food requirement
            session["food_requirement"] = user_msg_original if user_msg_original else "General food assistance"
            session["step"] = "completed"
            
            # Validate all required data is present before storing
            if not session.get("person_name") or session.get("age") is None or not session.get("location"):
                print(f"❌ Validation failed: Missing required fields")
                print(f"   Name: {session.get('person_name')}, Age: {session.get('age')}, Location: {session.get('location')}")
                return ChatResponse(
                    reply="I'm sorry, some information is missing. Please start a new conversation.",
                    session_id=session_id
                )
            
            # Log the data that will be stored
            print(f"\n{'='*60}")
            print(f"📝 Preparing to store food assistance request to Supabase...")
            print(f"   Session ID: {session_id}")
            print(f"   Name: {session['person_name']}")
            print(f"   Age: {session['age']}")
            print(f"   Location: {session['location']}")
            print(f"   Food Requirement: {session['food_requirement']}")
            print(f"   Assistance Type: {session['assistance_type']}")
            print(f"{'='*60}\n")
            
            # Store in Supabase FIRST (before webhook)
            stored = await store_in_supabase(session, session_id)
            
            # Trigger webhook AFTER successful storage (if stored)
            fulfillment_data = {
                "person_name": session["person_name"],
                "age": session["age"],
                "location": session["location"],
                "food_requirement": session["food_requirement"],
                "assistance_type": session["assistance_type"],
                "session_id": session_id
            }
            
            if stored:
                try:
                    await trigger_fulfillment_notification(fulfillment_data)
                    print(f"✅ Webhook notification sent successfully")
                except Exception as e:
                    print(f"⚠️ Webhook notification failed: {e}")
            
            # Prepare completion message
            response_text = f"Thank you {session['person_name']}! Your food assistance request has been confirmed. We're coordinating with our partners to ensure you receive food within 10 minutes. You will receive a confirmation shortly."
            
            if stored:
                response_text += " ✅ Your request has been saved in our system."
            else:
                response_text += " ⚠️ Note: There was an issue saving your request. Please contact support."
            
            return ChatResponse(reply=response_text, session_id=session_id)
        
        elif session["step"] == "completed":
            return ChatResponse(
                reply="Your request has already been processed. If you need another food assistance request, please start a new conversation.",
                session_id=session_id
            )
        
        else:
            # Fallback - unknown step, log and try to recover
            print(f"⚠️ Unknown step '{session['step']}' for session {session_id[:8]}...")
            # Don't reset to start, try to continue from current state
            session["step"] = "asking_name"  # Try to continue the flow
            return ChatResponse(
                reply="I'm here to help you get food assistance. Could you please tell me your name?",
                session_id=session_id
            )
    
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"❌ Error in chat_with_ai ({error_type}): {error_msg}")
        import traceback
        traceback.print_exc()
        return ChatResponse(
            reply="I'm sorry, I encountered an error. Please try again or contact support.",
            session_id=session_id
        )
