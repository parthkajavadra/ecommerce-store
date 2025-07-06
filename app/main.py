from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import user, product, cart,admin,seller, order
app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(user.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(admin.router)
app.include_router(seller.router)
app.include_router(order.router)
