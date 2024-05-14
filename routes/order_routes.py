from inspect import _empty
from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from models import Order, User, Product
from database import session, engine
from schemas import OrderModel, OrderStatusModel
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy import create_engine, null

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



@order_router.get("/{order_id}", status_code=status.HTTP_200_OK)
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



@order_router.get('/user/orders', status_code=status.HTTP_200_OK)
async def user_orders(Authorize: AuthJWT = Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    
    orders = session.query(Order).filter(Order.user_id == user.id).all()
    
    if orders is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orders not found")
    
    custom_data = [
        {
            "id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.value,
            "total_price": f"{order.quantity * order.product.price} UZS",
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



@order_router.get('/user/order/{order_id}', status_code=status.HTTP_200_OK)
async def user_order(order_id: int, Authorize: AuthJWT = Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    order = session.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    data = {
        "id": order.id,
        "quantity": order.quantity,
        "order_status": order.order_status.value,
        "total_price": f"{order.quantity * order.product.price} UZS",
        "product": {
            "id": order.product.id,
            "name": order.product.name,
            "description": order.product.description,
            "price": order.product.price
        }
    }
    return jsonable_encoder(data)


@order_router.put('/update/{order_id}', status_code=status.HTTP_200_OK)
async def update_udrt_order(order_id: int, update_order: OrderModel, Authorize: AuthJWT = Depends()):
    
    """Update user order"""
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    order = session.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
   
    order.quantity = update_order.quantity
    order.product_id = update_order.product_id
    
    session.commit()
    data = {
        "status": "success",
        "code": 200,
        "message": "User  order updated successfully",
        "data": {
            "id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.value,
            "total_price": f"{order.quantity * order.product.price} UZS",
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "description": order.product.description,
                "price": order.product.price
            }
        }
    }
    return jsonable_encoder(data)



@order_router.patch('/update-status/{order_id}', status_code=status.HTTP_200_OK)
async def update_order_status(order_id: int, status_order:OrderStatusModel, Authorize: AuthJWT = Depends()):
    """Update order status"""
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if user.is_staff == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not staff only staff can update order status")
    
    update_to_order = session.query(Order).filter(Order.id == order_id).first()
    
    if update_to_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    print("================================================================")
    print(status_order.order_status)
    
    update_to_order.order_status = status_order.order_status
    session.commit()
    
    current_response = {
        "status": "success",
        "code": 200,
        "message": "Order status updated successfully",
        "data": {
            "id": update_to_order.id,
            "quantity": update_to_order.quantity,
            "order_status": update_to_order.order_status.value  
        }
    }
    
    return jsonable_encoder(current_response)



@order_router.delete('/delete/{order_id}', status_code=status.HTTP_200_OK)
async def delete_order(order_id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    order = session.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.order_status != 'PENDING':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't delete '{order.order_status}' status order")
    
    session.delete(order)
    session.commit()
    
    custom_response = {
        "status": "success",
        "code": 200,
        "message": "Order deleted successfully"
    }
    
    return jsonable_encoder(custom_response)
    