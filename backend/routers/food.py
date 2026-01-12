from fastapi import APIRouter

router = APIRouter()  # This line MUST exist

# Your existing routes go here, using @router.get/post/etc
@router.get("/test")
def test():
    return {"message": "Food router works!"}
