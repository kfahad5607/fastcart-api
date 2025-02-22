from fastapi import FastAPI
from api.v1.routes import products

app = FastAPI(debug=True)

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
