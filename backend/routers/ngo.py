from fastapi import APIRouter

router = APIRouter()

@router.get("/ngo-example")
def ngo_example():
    return {"message": "Hello from NGO router!"}
