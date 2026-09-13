import requests
from datetime import datetime


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

    return (
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


def get_price(car):
    code = car["detail"]["code"]
    price = car["price"]
    price_type = price["type"]
    payment = price["payment"]
    prepayment = price["prepayment"]
    prepayment_primary = price["prepayment_primary"]
    prepayment_secondary = price["prepayment_secondary"]
    payment_primary = price["payment_primary"]
    delivery_days = price["delivery_days"]
    month_number = price["month_number"]

    return (
        code,
        price_type,
        price,
        prepayment,
        payment,
        prepayment,
        prepayment_primary,
        prepayment_secondary,
        payment_primary,
        delivery_days,
        month_number,
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
    return (id, address, dealer_name, score, dealer_type)


def all_cars_detail(cars):
    cars_list = []
    for i in cars:
        k = get_detail(i)
        cars_list.append(k)
    return cars_list


all_car = []
for page in range(0, 5):
    response = requests.get(
        f"https://bama.ir/cad/api/search?pageIndex={page}&pageSize=12"
    )

    if response.status_code == 200:
        data = response.json()
        data2 = data["data"]
        ads = data2["ads"]
        ads = list(filter(lambda x: x["type"] == "ad", ads))
        ads_car = all_cars_detail(ads)
        all_car += ads_car
