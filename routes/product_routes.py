from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from models import  User, Product
from database import session, engine
from schemas import ProductModel
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy import create_engine

product_router = APIRouter(
    prefix="/product",
    tags=["product"],
    responses={404: {"description": "Not found"}},
)   


session = session(bind=engine)

@product_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductModel, Authorize: AuthJWT=Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not allowed to create product")
    
    
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )

    session.add(new_product)
    session.commit()
    
    data = {
        "status": "success",
        "code": 201,
        "message": "Product created successfully",
        "data": {
            "id": new_product.id,
            "name": new_product.name,
            "description": new_product.description,
            "price": new_product.price,
            "quantity": new_product.quantity,
            "image": new_product.image
        }
    }

    return jsonable_encoder(data)

@product_router.get("/list", status_code=status.HTTP_200_OK)
async def get_all_products(Authorize: AuthJWT = Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not allowed to view products")
    
    
    
    products = session.query(Product).all()
    custom_data = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "image": product.image
        }
        for product in products
    ]
            
    data = {
        "status": "success",
        "code": 200,
        "message": "Products fetched successfully",
        "data": custom_data
    }
    return jsonable_encoder(data)


@product_router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int, Authorize: AuthJWT = Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not allowed to view products")
    
    product = session.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    data = {
        "status": "success",
        "code": 200,
        "message": "Product fetched successfully",
        "data": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "image": product.image
        }
    }    
    
    return jsonable_encoder(data)


@product_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, Authorize: AuthJWT = Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not allowed to delete products")
    
    product = session.query(Product).filter(Product.id == product_id).first()
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    session.delete(product)
    session.commit()
    
    data = {
        "status": "success",
        "code": 204,
        "message": "Product deleted successfully"
    }
    
    return jsonable_encoder(data)


@product_router.put("/{product_id}", status_code=status.HTTP_200_OK)
async def update_product(product_id: int, update_product: ProductModel, Authorize: AuthJWT = Depends()):
    
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not allowed to update products")
    
    product = session.query(Product).filter(Product.id == product_id).first()
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    for key, value in update_product.dict(exclude_unset=True).items():
        setattr(product, key, value)
    session.commit()
    
    data = {
        "status": "success",
        "code": 200,
        "message": "Product updated successfully",
        "data": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity
        }
    }
    
    return jsonable_encoder(data)
    