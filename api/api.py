from fastapi import FastAPI

app = FastAPI()


@app.get("/cars")
async def get_cars(page: int, limit: int):
    pass


@app.get("/cars/{car_code}")
async def get_car(car_code):
    pass
