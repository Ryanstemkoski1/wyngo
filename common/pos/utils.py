import json


def print_json(payload):
    json_string = json.dumps(payload, indent=4)
    print(json_string)


def filter(items, key, value=None):
    if not value:
        return [item for item in items if key in item]

    return [item for item in items if item.get(key) == value]


def search(items, key, value=None):
    if not value:
        return next((item[key] for item in items), {})

    return next((item for item in items if item.get(key) == value), {})


def get_price_range(products):
    min_price = min(product["price"] for product in products)
    max_price = max(product["price"] for product in products)

    if max_price == min_price:
        return {"max_price": max_price, "min_price": 0}

    return {"max_price": max_price, "min_price": min_price}


def format_price(price):
    price = f"{(price // 100)}.{(price % 100):02}"
    return float(price)


def get_product_prices(products):
    if len(products) > 1:
        price_range = get_price_range(products)
        return {
            **price_range,
            "price": 0,  # No price is needed if there is a price range
        }
    else:
        return {"min_price": 0, "max_price": 0, "price": products[0].get("price", 0)}
