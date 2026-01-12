# routers/referral.py (example)
from fastapi import APIRouter

router = APIRouter()  # must be named 'router'

@router.get("/referral-example")
def referral_example():
    return {"message": "Referral endpoint works!"}
