import datetime
from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from schemas import SignUpModel, LoginModel
from database import session, engine
from models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)  
session = session(bind=engine)
Authorize = AuthJWT()

@auth_router.get("/")
async def welcome(Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing or invalid")

    return {"message": "Signup sahifasiga xush kelibsiz "}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):

    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    new_user = User(
        username=user.username, 
        email=user.email, 
        password=generate_password_hash(user.password),
        is_staff= user.is_staff,
        is_active= user.is_active
    )

    session.add(new_user)
    session.commit()
    data = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_staff": new_user.is_staff,
        "is_active": new_user.is_active
    }

    response_model = {
        "status": "success",
        "message": "User created successfully", 
        "code": status.HTTP_201_CREATED,
        "data": data
    }

    return response_model 

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: LoginModel, Authorize: AuthJWT=Depends()):
    
    db_user = session.query(User).filter(or_
    (User.username == user.username_or_email, 
    User.email == user.username_or_email)).first()

    if db_user is None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")

    if not check_password_hash(db_user.password, user.password):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")

    access_lifetime = datetime.timedelta(minutes=60) # Token muddati
    refresh_lifetime = datetime.timedelta(days=3) # Refresh token muddati
        
    access_token = Authorize.create_access_token(subject=db_user.username, expires_time = access_lifetime)
    refresg_token = Authorize.create_refresh_token(subject=db_user.username, expires_time = refresh_lifetime)

    token = {
        "access_token": access_token,
        "refresh_token": refresg_token
    }

    response = {
        "status": "success",
        "message": "User logged in successfully",
        "code": status.HTTP_200_OK,
        "data": token
    }
    return jsonable_encoder(response)


@auth_router.get("/login/refresh")
async def refresh_token(Authorize: AuthJWT=Depends()):

    try:
        access_lifetime = datetime.timedelta(minutes=60) # Token muddati
        
        Authorize.jwt_refresh_token_required() # Valid access token talab qilinadi
        current_user = Authorize.get_jwt_subject() # Token ichida username ni olish

        db_user = session.query(User).filter(User.username == current_user).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

        new_access_token = Authorize.create_access_token(subject=db_user.username, expires_time = access_lifetime) # Token yaratish
        response = {
            "status": "success",
            "message": "News access token created successfully",
            "code": status.HTTP_200_OK,
            "data": {
               "access_token": new_access_token
            }
        }
        return jsonable_encoder(response)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token is missing or invalid")