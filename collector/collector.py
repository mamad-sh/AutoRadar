import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import mysql.connector


def get_detail(car):

    detail = car["detail"]

    # start detail
    code = detail["code"]

    brand = detail["brand"]
    brand_fa = detail["brand_fa"]
    trim = detail["trim"]
    title = detail["title"]
    year = int(detail["year"])
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
    try:
        mileage = int(detail["mileage"].replace(",", "").replace("km", ""))
    except:
        mileage = 0

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
    # Normalize price fields to integers for comparison in insert_into_prices
    price = int(price.replace(",", ""))
    prepayment = int(prepayment.replace(",", ""))
    prepayment_primary = int(prepayment_primary.replace(",", ""))
    prepayment_secondary = int(prepayment_secondary.replace(",", ""))
    payment = int(payment.replace(",", ""))
    payment_primary = int(payment_primary.replace(",", ""))

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
    else:
        return


def all_cars_detail():
    with ThreadPoolExecutor(max_workers=3) as executer:
        while True:

            car = cars.get()

            if car is None:

                dealers.put(None)
                prices.put(None)
                details.put(None)
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


def insert_into_dealers():

    q = """
    INSERT INTO dealers (id, address, name, score, type)
    VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
        address = VALUES(address),
        name = VALUES(name),
        score = VALUES(score),
        type = VALUES(type)
    """
    cnx = mysql.connector.connect(
        host="127.0.0.1", user="root", password="m13910110sh", database="autocar"
    )
    while True:
        dealer = dealers.get()

        if dealer is None:

            dealers.task_done()
            cnx.close()
            break

        cursor = cnx.cursor()
        cursor.execute(q, dealer)
        cnx.commit()
        cursor.close()

        dealers.task_done()


def insert_into_details():

    q = """
    INSERT INTO cars (
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
    dealer_id
    )
    VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        brand = VALUES(brand),
        brand_fa = VALUES(brand_fa),
        trim = VALUES(trim),
        title = VALUES(title),
        year = VALUES(year),
        mileage = VALUES(mileage),
        location = VALUES(location),
        body_color = VALUES(body_color),
        body_status = VALUES(body_status),
        body_type = VALUES(body_type),
        body_type_fa = VALUES(body_type_fa),
        fuel = VALUES(fuel),
        transmission = VALUES(transmission),
        description = VALUES(description),
        url = VALUES(url),
        modified_date = VALUES(modified_date),
        dealer_id = VALUES(dealer_id)
    """
    cnx = mysql.connector.connect(
        host="127.0.0.1", user="root", password="m13910110sh", database="autocar"
    )
    while True:
        detail = details.get()

        if detail is None:

            details.task_done()
            cnx.close()
            break
        cursor = cnx.cursor()
        cursor.execute(q, detail)

        cnx.commit()
        cursor.close()
        details.task_done()


def insert_into_prices():
    query_insert_to_history = """
    INSERT INTO price_history (
        car_code,
        type,
        price,
        prepayment,
        payment,
        prepayment_primary,
        prepayment_secondary,
        payment_primary,
        delivery_days,
        month_number,
        recorded_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    query_find_last_snapshot = """
    SELECT *
    FROM price_history
    WHERE car_code = %s
    ORDER BY recorded_at DESC
    LIMIT 1;
    """
    query_insert_to_prices = """
    INSERT INTO prices (
        car_code,
        type,
        price,
        prepayment,
        payment,
        prepayment_primary,
        prepayment_secondary,
        payment_primary,
        delivery_days,
        month_number
        ) 
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
        type = VALUES(type),
        price = VALUES(price),
        prepayment = VALUES(prepayment),
        payment = VALUES(payment),
        prepayment_primary = VALUES(prepayment_primary),
        prepayment_secondary = VALUES(prepayment_secondary),
        payment_primary = VALUES(payment_primary),
        delivery_days = VALUES(delivery_days),
        month_number = VALUES(month_number)
    """
    cnx = mysql.connector.connect(
        host="127.0.0.1", user="root", password="m13910110sh", database="autocar"
    )

    while True:

        price = prices.get()

        if price is None:

            cnx.close()
            prices.task_done()

            break

        # cursors
        cursor = cnx.cursor()
        cursor_history = cnx.cursor()

        # get last snapshot
        cursor_history.execute(query_find_last_snapshot, (price[0],))
        last_history = cursor_history.fetchone()

        # check last snapshot is none if not slice it
        if last_history is not None:
            last_history = last_history[1:-1]

        # Compare the latest snapshot with the new price and insert to history

        if last_history != price:
            new_history = price + (datetime.now(),)
            cursor_history.execute(query_insert_to_history, new_history)

        # insert new price to prices
        cursor.execute(query_insert_to_prices, price)

        # commit and task done
        cnx.commit()

        cursor_history.close()
        cursor.close()

        prices.task_done()


with ThreadPoolExecutor(max_workers=3) as executer:
    cars = Queue()
    details = Queue()
    prices = Queue()
    dealers = Queue()
    futures = []
    executer.submit(all_cars_detail)
    for i in range(0, 4):
        future = executer.submit(ads_car, i)
        futures.append(future)

    for future in futures:
        future.result()
    cars.put(None)

    executer.submit(insert_into_dealers)
    dealers.join()
    executer.submit(insert_into_details)

    details.join()
    executer.submit(insert_into_prices)
    prices.join()
