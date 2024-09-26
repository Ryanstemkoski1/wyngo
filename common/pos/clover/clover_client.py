import time

from requests import request

from wyndo.settings import CLOVER_URL


class CloverRequestClient:
    HOST = CLOVER_URL
    HEADERS = {
        "Content-Type": "application/json",
    }

    def __init__(self, access_token, merchand_id):
        self._merchant_id = merchand_id
        self._access_token = access_token
        self._call_count = 0
        self._last_call_timestamp = time.time()

    def _rate_limit_check(self):
        current_time = time.time()
        if current_time - self._last_call_timestamp < 1:
            self._call_count += 1
            if self._call_count >= 16:
                sleep_duration = 1 - (current_time - self._last_call_timestamp)
                time.sleep(sleep_duration)
                self._call_count = 0
                self._last_call_timestamp = time.time()
        else:
            self._call_count = 1
            self._last_call_timestamp = current_time

    def _request(self, path, method="GET", params={}, json=None):
        self._rate_limit_check()

        headers = self.HEADERS.copy()
        headers["Authorization"] = f"Bearer {self._access_token}"
        response = request(
            method=method,
            url=f"{self.HOST}/v3/merchants/{path}",
            json=json,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def get_items(self, item_id: str = None, limit=100, offset=0):
        params = {
            "expand": "tags,categories,taxRates,modifierGroups,itemStock,item",
        }

        path = f"{self._merchant_id}/items"

        if item_id is None:
            params["offset"] = offset
            params["limit"] = limit
        else:
            path += f"/{item_id}"

        result = self._request(path=path, params=params)
        return result

    def get_item_group(self, group_id):
        path = f"{self._merchant_id}/item_groups/{group_id}"
        return self._request(path=path)

    def get_inventory(self, limit: int = 100, offset: int = 0):
        try:
            items = self.get_items(limit=limit, offset=offset)
            if not items:
                return []

            return items

        except Exception as e:
            raise e

    def get_single_item(self, item_id: str):
        try:
            items = {"elements": [self.get_items(item_id=item_id)]}
            if not items:
                return []

            return items

        except Exception as e:
            raise e

    def create_order(self, payload):
        path = f"{self._merchant_id}/atomic_order/orders/"
        return self._request(path=path, method="POST", json=payload)

    def update_order(self, order_id, payload):
        path = f"{self._merchant_id}/orders/{order_id}?expand=lineItems"
        return self._request(path=path, method="POST", json=payload)

    def add_line_item(self, order_id, payload):
        path = f"{self._merchant_id}/orders/{order_id}/line_items"
        return self._request(path=path, method="POST", json=payload)

    def remove_line_items(self, order_id):
        path = f"{self._merchant_id}/orders/{order_id}/line_items"
        return self._request(path, method="DELETE")

    def delete_order(self, order_id):
        path = f"{self._merchant_id}/orders/{order_id}"
        return self._request(path=path, method="DELETE")

    def create_item(self, product):
        path = f"{self._merchant_id}/items/"
        item = self._request(
            path=path,
            method="POST",
            json={
                "hidden": "false",
                "available": "true",
                "name": product.name,
                "price": int(product.min_price) * 100,
                "stockCount": product.total_stock,
            }
        )
        return item

    def update_item(self, product):
        path = f"{self._merchant_id}/items/{product.origin_id}"
        item = self._request(
            path=path,
            method="POST",
            json={
                "hidden": "false",
                "available": "true",
                "name": product.name,
                "price": int(product.min_price) * 100,
                "stockCount": product.total_stock,
            }
        )
        return item

    def update_group_item(self, product):
        payload = {
            "name": product.name,
        }
        path = f"{self._merchant_id}/item_groups/{product.origin_id}"
        return self._request(
            path=path,
            method="POST",
            json=payload
        )
