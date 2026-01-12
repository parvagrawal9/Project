from fastapi import APIRouter

router = APIRouter()

@router.get("/subscription-example")
def subscription_example():
    return {"message": "Hello from subscription router!"}
