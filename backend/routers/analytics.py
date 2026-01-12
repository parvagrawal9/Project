from fastapi import APIRouter

router = APIRouter()

@router.get("/analytics-example")
def analytics_example():
    return {"message": "Hello from analytics router!"}
