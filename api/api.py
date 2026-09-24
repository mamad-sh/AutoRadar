from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/cars")
async def get_cars(page: int, limit: int):
    pass


@app.get("/cars/{car_code}")
async def get_car(car_code: str):
    pass


@app.get("/cars/search")
async def search_car(
    brand: str | None = None,
    max_price: int | None = None,
    min_year: int | None = None,
):
    return JSONResponse(
        {"brand": brand, "max_price": max_price, "min_year": min_year},
        status_code=status.HTTP_200_OK,
    )


@app.get("/cars/{car_code}/price_history")
async def car_price_history(car_code: str):
    return JSONResponse({"detail": "True"}, status_code=status.HTTP_200_OK)
