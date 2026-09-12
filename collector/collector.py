import requests


def get_detail(car):
    detail = car["detail"]
    price = car["price"]
    specs = car["specs"]
    dealer = car["dealer"]

    # start detail
    code = detail["code"]
    title = detail["title"]
    body_status = detail["body_status"]
    body_color = detail["body_color"]
    fuel_type = detail["fuel"]
    karkard = detail["mileage"]
    year = detail["year"]
    dande = detail["transmission"]
    location = detail["location"]
    # end detail

    # start engine
    acceleration = specs["acceleration"]
    engine = specs["engine"]
    volume = specs["volume"]
    fuel_consumed_in_100km = specs["fuel"]
    # end engine

    # start price
    price_type = price["type"]
    payment = 0
    prepayment = 0
    price_txt = 0
    if price_type == "negotiable":
        price_txt = "توافقی"
    if price_type == "lumpsum":
        price_txt = price["price"]
    if price_type == "installemnt":
        price_txt = price["price"]
        payment = price["payment"]
        prepayment = price["prepayment"]
    # end price

    # start dealer

    dealer_name = None
    dealer_type = None
    if dealer != None:
        dealer_name = dealer["name"]
        dealer_type = dealer["type"]
    # end dealer

    return (
        title,
        body_status,
        body_color,
        fuel_type,
        karkard,
        year,
        dande,
        location,
        acceleration,
        engine,
        volume,
        fuel_consumed_in_100km,
        price_type,
        price_txt,
        prepayment,
        payment,
        dealer_type,
        dealer_name,
    )


def all_cars_detail(cars):
    cars_list = []
    for i in cars:
        k = get_detail(i)
        cars_list.append(k)
    return cars_list


all_car = []
for page in range(0, 12):
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
