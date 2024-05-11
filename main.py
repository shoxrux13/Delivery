from fastapi import FastAPI
from routes import order_routes, auth_routes, product_routes
from fastapi_jwt_auth import AuthJWT
from schemas import Settings, LoginModel

app = FastAPI()

@AuthJWT.load_config
def get_config():
    return Settings()

app.include_router(order_routes.order_router)
app.include_router(auth_routes.auth_router)
app.include_router(product_routes.product_router)

@app.get("/")
async def root():
    return {"Hello": "World"}