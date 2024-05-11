from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from models import Order, User, Product
from database import session, engine
from schemas import OrderModel, OrderStatusModel
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy import create_engine

order_router = APIRouter(
    prefix="/order",
    tags=["order"],
    responses={404: {"description": "Not found"}},
)   


session = session(bind=engine)

@order_router.get("/")
async def welcome(Authorize: AuthJWT=Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    return {"message": "Welcome to the order page"}




#Yangi buyurtma yaratish
@order_router.post("/make", status_code=status.HTTP_201_CREATED)
async def make_order(order: OrderModel, Authorize: AuthJWT=Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    new_order = Order(
        quantity=order.quantity,
        product_id=order.product_id
    )

    new_order.user = user
    session.add(new_order)
    session.commit()
    
    data = {
        "status": "success",
        "code": 201,
        "message": "Order created successfully",
        "data": {
            "id": new_order.id,
            "quantity": new_order.quantity,
            "order_status": new_order.order_status,
            "total_price": f"{new_order.quantity * new_order.product.price} UZS",
            "product": {
                "id": new_order.product.id,
                "name": new_order.product.name,
                "description": new_order.product.description,
                "price": new_order.product.price
            }
        }
    }
    return jsonable_encoder(data)





@order_router.get("/list")
async def all_order_list(Authorize: AuthJWT=Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if user.is_staff == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not staff only staff can see all orders")
    
    orders = session.query(Order).all()
    custom_data = [
        {
            "id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.value,
            "total_price": f"{order.quantity * order.product.price} UZS",
            "user": {
                "id": order.user.id,
                "username": order.user.username
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "description": order.product.description,
                "price": order.product.price
            }
        }
        for order in orders
    ]
    return jsonable_encoder(custom_data)




@order_router.get("/{order_id}")
async def get_order_by_id(order_id: int, Authorize: AuthJWT=Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.is_staff == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not staff only staff can see this order")
    
    order = session.query(Order).filter(Order.id == order_id).first()
    
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    data = {
        "id": order.id,
        "quantity": order.quantity,
        "order_status": order.order_status.value,
        "total_price": f"{order.quantity * order.product.price} UZS",
        "user": {
            "id": order.user.id,
            "username": order.user.username
        },
        "product": {
            "id": order.product.id,
            "name": order.product.name,
            "description": order.product.description,
            "price": order.product.price
        }
    }
    return jsonable_encoder(data)