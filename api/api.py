from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import mysql.connector

app = FastAPI()

pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="autoradar_pool",
    pool_size=5,
    host="127.0.0.1",
    user="root",
    password="m13910110sh",
    database="autocar",
)


@app.get("/cars")
async def get_cars(page: int, limit: int):
    conn = pool.get_connection()
    query = """SELECT cars.code,cars.brand,cars.brand_fa,cars.title,cars.year,
    cars.mileage,cars.location,prices.price,prices.type,prices.payment,
    prices.prepayment,dealers.address,dealers.name,dealers.score,dealers.type
FROM cars
JOIN prices ON cars.code = prices.car_code
LEFT jOIN dealers ON cars.dealer_id = dealers.id
ORDER BY modified_date DESC
LIMIT %s OFFSET %s;
"""

    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, (limit, ((page - 1) * limit)))
    cars = cursor.fetchall()
    for car in cars:
        if car["score"] is not None:
            car["score"] = float(car["score"])
    conn.close()
    return JSONResponse(cars, status_code=status.HTTP_200_OK)


@app.get("/cars/{car_code}")
async def get_car(car_code: str):
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """SELECT cars.code,
    cars.brand,
    cars.brand_fa,
    cars.trim,
    cars.title,
    cars.year,
    cars.mileage,
    cars.location,
    cars.body_color,
    cars.body_status,
    cars.body_type,
    cars.body_type_fa,
    cars.fuel,
    cars.transmission,
    cars.description,
    cars.url,
    cars.modified_date,
    cars.dealer_id,
    prices.price,
    prices.prepayment,
    prices.payment,
    prices.prepayment_primary,
    prices.prepayment_secondary,
    prices.payment_primary,
    prices.delivery_days,
    prices.month_number,
    dealers.type,
    dealers.address,
    dealers.name,
    dealers.score 
    FROM cars
    JOIN prices ON cars.code = prices.car_code
    LEFT JOIN dealers ON cars.dealer_id = dealers.id
    WHERE code = %s;
"""
    cursor.execute(query, (car_code,))
    car = cursor.fetchone()
    car["modified_date"] = str(car["modified_date"])
    if car["score"] is not None:
        car["score"] = float(car["score"])
    return JSONResponse(car, status_code=status.HTTP_200_OK)


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
