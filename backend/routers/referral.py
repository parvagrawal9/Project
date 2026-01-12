from fastapi import APIRouter

router = APIRouter()

@router.get("/referral-example")
def referral_example():
    return {"message": "Hello from referral router!"}
