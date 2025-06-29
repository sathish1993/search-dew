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
            resp.raise_for_status() # Raise an exception for bad status codes
            current_page_items = resp.json()

            if not current_page_items:
                # No more items, so break the loop
                break

            all_items.extend(current_page_items)
            offset += limit
            print(f"Fetched {len(current_page_items)} items. Total so far: {len(all_items)}")

            # Be a good citizen: add a small delay to avoid hitting rate limits
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break # Exit on error

    return all_items

