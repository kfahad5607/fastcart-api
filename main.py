from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.v1.routes import products
from models.products import Product
from models.orders import Order, OrderItem
from db.sql import init_db
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("server is starting")
    await init_db()
    yield
    logger.critical("server is shutting down")

app = FastAPI(debug=True, lifespan=lifespan)

# Include routers
app.include_router(
    products.router, 
    prefix="/api/v1/products", 
    tags=["products"]
)
app.include_router(
    products.router, 
    prefix="/api/v1/orders", 
    tags=["orders"]
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
