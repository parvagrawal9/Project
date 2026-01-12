"""
LangGraph workflow for food assistance conversation flow
"""
from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
import json
from datetime import datetime
from supabase_client import supabase
import asyncio
from fulfillment import trigger_fulfillment_notification


class ConversationState(TypedDict):
    """State for the conversation workflow"""
    messages: Annotated[list, add_messages]
    intent: Literal["immediate_food", "scheduled_food", "ngo_referral", None]
    person_name: str | None
    age: int | None
    location: str | None
    food_requirement: str | None
    session_id: str | None
    assistance_type: Literal["immediate", "scheduled", "ngo_referral"] | None
    fulfillment_triggered: bool


def start_node(state: ConversationState) -> ConversationState:
    """Receive user input and forward to router"""
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            # Forward message to router
            return state
    return state


def router_node(state: ConversationState) -> ConversationState:
    """Classify intent based on user message"""
    messages = state.get("messages", [])
    if not messages:
        return state
    
    last_message = messages[-1]
    if not isinstance(last_message, HumanMessage):
        return state
    
    user_message = last_message.content.lower()
    
    # Routing rules
    urgent_keywords = ["hungry", "starving", "need food now", "urgent", "immediate", "emergency", "asap"]
    scheduled_keywords = ["later", "tomorrow", "next week", "schedule", "plan"]
    ngo_keywords = ["ngo", "referral", "support", "help", "assistance", "organization"]
    
    intent = None
    if any(keyword in user_message for keyword in urgent_keywords):
        intent = "immediate_food"
    elif any(keyword in user_message for keyword in scheduled_keywords):
        intent = "scheduled_food"
    elif any(keyword in user_message for keyword in ngo_keywords):
        intent = "ngo_referral"
    else:
        # Default to immediate if no clear intent
        intent = "immediate_food"
    
    state["intent"] = intent
    
    # Determine assistance type
    if intent == "immediate_food":
        state["assistance_type"] = "immediate"
    elif intent == "scheduled_food":
        state["assistance_type"] = "scheduled"
    else:
        state["assistance_type"] = "ngo_referral"
    
    return state


def immediate_food_node(state: ConversationState) -> ConversationState:
    """Handle immediate food assistance request"""
    return collect_user_info(state, "immediate")


def scheduled_food_node(state: ConversationState) -> ConversationState:
    """Handle scheduled food assistance request"""
    return collect_user_info(state, "scheduled")


def ngo_referral_node(state: ConversationState) -> ConversationState:
    """Handle NGO referral request"""
    return collect_user_info(state, "ngo_referral")


def collect_user_info(state: ConversationState, assistance_type: str) -> ConversationState:
    """Collect required user information one field at a time"""
    messages = state.get("messages", [])
    person_name = state.get("person_name")
    age = state.get("age")
    location = state.get("location")
    food_requirement = state.get("food_requirement")
    
    # Check what's missing
    missing_fields = []
    if not person_name:
        missing_fields.append("person_name")
    if age is None:
        missing_fields.append("age")
    if not location:
        missing_fields.append("location")
    if not food_requirement:
        missing_fields.append("food_requirement")
    
    # If all fields collected, trigger fulfillment
    if not missing_fields:
        if not state.get("fulfillment_triggered", False):
            trigger_fulfillment(state, assistance_type)
            state["fulfillment_triggered"] = True
            response = "Thank you! Your food assistance request has been confirmed. We're coordinating with our partners to ensure you receive food within 10 minutes. You will receive a confirmation shortly."
            state["messages"].append(AIMessage(content=response))
        return state
    
    # Extract information from last message if available
    if messages:
        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            user_text = last_message.content.strip()
            
            # Try to extract name - improved logic
            if not person_name:
                import re
                # Patterns: "I'm John", "My name is John", "I am John", "name is John", "called John"
                name_patterns = [
                    r"(?:i'?m|i am|my name is|name is|called|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
                    r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$"  # If entire message is just a name
                ]
                for pattern in name_patterns:
                    match = re.search(pattern, user_text, re.IGNORECASE)
                    if match:
                        potential_name = match.group(1).strip()
                        if len(potential_name.split()) <= 3:  # Reasonable name length
                            person_name = potential_name
                            state["person_name"] = person_name
                            break
                
                # If still no name and message is short, might be just the name
                if not person_name and len(user_text.split()) <= 3 and user_text.replace(" ", "").isalpha():
                    person_name = user_text.strip()
                    state["person_name"] = person_name
            
            # Try to extract age - improved logic
            if age is None:
                import re
                # Patterns: "I am 25", "age is 25", "25 years old", "25"
                age_patterns = [
                    r"(?:i am|age is|i'?m|years old|year old)\s+(\d{1,3})",
                    r"\b(\d{1,3})\s*(?:years?|yrs?|old)?\b",
                    r"^(\d{1,3})$"  # If entire message is just a number
                ]
                for pattern in age_patterns:
                    match = re.search(pattern, user_text, re.IGNORECASE)
                    if match:
                        potential_age = int(match.group(1))
                        if 1 <= potential_age <= 120:
                            age = potential_age
                            state["age"] = age
                            break
            
            # Try to extract location - improved logic
            if not location:
                import re
                # Patterns: "I live in...", "location is...", "address is...", "at...", "in..."
                location_patterns = [
                    r"(?:i live in|location is|address is|i am at|i am in|at|in|near|area is|located at)\s+(.+)",
                    r"^(.+)$"  # If asked for location, entire message might be location
                ]
                for pattern in location_patterns:
                    match = re.search(pattern, user_text, re.IGNORECASE)
                    if match:
                        potential_location = match.group(1).strip()
                        # Remove common prefixes
                        potential_location = re.sub(r"^(i live in|location is|address is|i am at|i am in|at|in|near|area is|located at)\s+", "", potential_location, flags=re.IGNORECASE)
                        if len(potential_location) > 3:  # Reasonable location length
                            location = potential_location
                            state["location"] = location
                            break
            
            # Try to extract food requirement - if it's a longer message and other fields are filled
            if not food_requirement and person_name and age is not None and location:
                # If we have other info and this is a longer message, likely food requirement
                if len(user_text) > 10:
                    food_requirement = user_text
                    state["food_requirement"] = food_requirement
    
    # Ask for missing field (one at a time) - improved prompts
    if not person_name:
        response = "Hello! I'm here to help you get food assistance. To proceed, I need a few details. Could you please tell me your name?"
    elif age is None:
        response = f"Thank you, {person_name}! Could you please tell me your age?"
    elif not location:
        response = f"Thank you! Could you please tell me your location or area where you need the food delivered?"
    elif not food_requirement:
        response = "Great! Could you please tell me what kind of food you need or any specific requirements?"
    else:
        response = "Thank you for providing all the information!"
    
    state["messages"].append(AIMessage(content=response))
    return state


def trigger_fulfillment(state: ConversationState, assistance_type: str) -> None:
    """Trigger fulfillment process when all data is collected"""
    person_name = state.get("person_name")
    age = state.get("age")
    location = state.get("location")
    food_requirement = state.get("food_requirement")
    session_id = state.get("session_id", "unknown")
    
    # Prepare fulfillment data
    fulfillment_data = {
        "person_name": person_name,
        "age": age,
        "location": location,
        "food_requirement": food_requirement,
        "assistance_type": assistance_type,
        "session_id": session_id
    }
    
    # Store in Supabase
    if supabase:
        try:
            supabase_data = {
                "person_name": person_name,
                "age": age,
                "location": location,
                "food_request": food_requirement,
                "assistance_type": assistance_type,
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            result = supabase.table("food_assistance_requests").insert(supabase_data).execute()
            print(f"Data stored in Supabase: {result}")
            
        except Exception as e:
            print(f"Error storing fulfillment data in Supabase: {e}")
            # Continue even if Supabase fails
    else:
        print(f"Supabase not configured. Fulfillment data (not stored): {fulfillment_data}")
    
    # Trigger fulfillment notification
    try:
        # Use asyncio to run async function
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is already running, schedule the coroutine
            asyncio.create_task(trigger_fulfillment_notification(fulfillment_data))
        else:
            loop.run_until_complete(trigger_fulfillment_notification(fulfillment_data))
    except Exception as e:
        print(f"Error triggering fulfillment notification: {e}")
        # Continue even if notification fails


def should_continue(state: ConversationState) -> Literal["collect_info", "end"]:
    """Determine if we should continue collecting info or end"""
    person_name = state.get("person_name")
    age = state.get("age")
    location = state.get("location")
    food_requirement = state.get("food_requirement")
    fulfillment_triggered = state.get("fulfillment_triggered", False)
    
    if fulfillment_triggered:
        return "end"
    
    if person_name and age is not None and location and food_requirement:
        return "end"
    
    return "collect_info"


# Build the graph
def create_workflow():
    """Create the LangGraph workflow"""
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("start", start_node)
    workflow.add_node("router", router_node)
    workflow.add_node("immediate_food", immediate_food_node)
    workflow.add_node("scheduled_food", scheduled_food_node)
    workflow.add_node("ngo_referral", ngo_referral_node)
    
    # Set entry point
    workflow.set_entry_point("start")
    
    # Add edges
    workflow.add_edge("start", "router")
    
    # Conditional routing from router
    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("intent", "immediate_food"),
        {
            "immediate_food": "immediate_food",
            "scheduled_food": "scheduled_food",
            "ngo_referral": "ngo_referral"
        }
    )
    
    # All assistance nodes can continue or end
    workflow.add_conditional_edges(
        "immediate_food",
        should_continue,
        {
            "collect_info": "immediate_food",  # Loop back to continue collecting
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "scheduled_food",
        should_continue,
        {
            "collect_info": "scheduled_food",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "ngo_referral",
        should_continue,
        {
            "collect_info": "ngo_referral",
            "end": END
        }
    )
    
    return workflow.compile()


# Global workflow instance
workflow = create_workflow()
