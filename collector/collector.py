import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue


def get_detail(car):

    detail = car["detail"]

    # start detail
    code = detail["code"]

    brand = detail["brand"]
    brand_fa = detail["brand_fa"]
    trim = detail["trim"]
    title = detail["title"]
    year = detail["year"]
    mileage = detail["mileage"]
    location = detail["location"]
    body_color = detail["body_color"]
    body_status = detail["body_status"]
    body_type = detail["body_type"]
    body_type_fa = detail["body_type_fa"]
    fuel = detail["fuel"]
    transmission = detail["transmission"]
    description = detail["description"]
    url = detail["url"]
    modified_date = datetime.fromisoformat(detail["modified_date"])
    if car["dealer"] != None:
        dealer_id = car["dealer"]["id"]
    else:
        dealer_id = None

    # end detail
    details.put(
        (
            code,
            brand,
            brand_fa,
            trim,
            title,
            year,
            mileage,
            location,
            body_color,
            body_status,
            body_type,
            body_type_fa,
            fuel,
            transmission,
            description,
            url,
            modified_date,
            dealer_id,
        )
    )


def get_price(car):
    code = car["detail"]["code"]
    price_dict = car["price"]
    price = price_dict["price"]
    price_type = price_dict["type"]
    payment = price_dict["payment"]
    prepayment = price_dict["prepayment"]
    prepayment_primary = price_dict["prepayment_primary"]
    prepayment_secondary = price_dict["prepayment_secondary"]
    payment_primary = price_dict["payment_primary"]
    delivery_days = price_dict["delivery_days"]
    month_number = price_dict["month_number"]
    price = int(price.replace(",", ""))
    prices.put(
        (
            code,
            price_type,
            price,
            prepayment,
            payment,
            prepayment_primary,
            prepayment_secondary,
            payment_primary,
            delivery_days,
            month_number,
        )
    )


def get_dealer(car):
    dealer = car["dealer"]
    dealer_name = None
    dealer_type = None
    score = None
    id = None
    address = None
    if dealer != None:
        dealer_name = dealer["name"]
        dealer_type = dealer["type"]
        score = dealer["score"]
        id = dealer["id"]
        address = dealer["address"]
    dealers.put((id, address, dealer_name, score, dealer_type))


def all_cars_detail():
    with ThreadPoolExecutor(max_workers=3) as executer:
        while True:
            car = cars.get()
            if car is None:
                cars.task_done()
                break

            dealer_future = executer.submit(get_dealer, car)
            detail_future = executer.submit(get_detail, car)
            price_future = executer.submit(get_price, car)

            detail_future.result()
            dealer_future.result()
            price_future.result()
            cars.task_done()


def ads_car(page):
    response = requests.get(
        f"https://bama.ir/cad/api/search?pageIndex={page}&pageSize=12"
    )

    if response.status_code == 200:
        data = response.json()
        data2 = data["data"]
        ads = data2["ads"]
        ads = list(filter(lambda x: x["type"] == "ad", ads))
        for car in ads:
            cars.put(car)


with ThreadPoolExecutor(max_workers=2) as executer:
    cars = Queue()
    details = Queue()
    prices = Queue()
    dealers = Queue()
    futures = []
    executer.submit(all_cars_detail)
    for i in range(0, 1):
        future = executer.submit(ads_car, 0)
        futures.append(future)

    for future in futures:
        future.result()
    cars.put(None)
    cars.join()

    print(list(details.queue), list(prices.queue), list(dealers.queue))
