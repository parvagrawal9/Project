from fastapi import APIRouter

router = APIRouter()  # This line MUST exist exactly like this

@router.get("/test")
def test():
    return {"message": "Auth router works!"}
