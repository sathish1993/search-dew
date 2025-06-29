import requests
import time


def fetch_all_archive_items():
    base_url = 'https://dataengineeringweekly.substack.com/api/v1/archive'
    all_items = []
    limit = 20
    offset = 0

    while True:
        params = {'limit': limit, 'offset': offset}
        try:
            resp = requests.get(base_url, params=params)
            resp.raise_for_status()
            current_page_items = resp.json()

            if not current_page_items:
                break

            all_items.extend(current_page_items)
            offset += limit
            print(f"Fetched {len(current_page_items)} items. Total so far: {len(all_items)}")

            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break

    return all_items

