from fastapi import APIRouter

order_router = APIRouter(
    prefix="/order",
    tags=["order"],
    responses={404: {"description": "Not found"}},
)   

@order_router.get("/")
async def order():
    return {"message": "Order"}
