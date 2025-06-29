import json
import os
import time
from get_article_links import fetch_all_archive_items

from bs4 import BeautifulSoup
import requests


def extract_article_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1').text if soup.find('h1') else 'No Title'
        article_body_tag = soup.find('div', class_='body')
        content_paragraphs = []
        if article_body_tag:
            for p in article_body_tag.find_all('p'):
                content_paragraphs.append(p.text)
        full_content = "\n".join(content_paragraphs)

        return {'url': url, 'title': title, 'content': full_content}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing content from {url}: {e}")
        return None


def get_data(file_path, content_path):
    if os.path.exists(file_path):
        print(f"{file_path} already exists.")
        with open(file_path, 'r') as f:
            data = json.load(f)
            all_documents = []
            for item in data:
                print("working on " + item['canonical_url'])
                if 'canonical_url' in item:
                    article_data = extract_article_content(item['canonical_url'])

                    if article_data and article_data['content']:
                        all_documents.append(article_data)
                        time.sleep(3)

            with open(content_path, 'w') as f:
                json.dump(all_documents, f)

            print(f"\nSuccessfully fetched contents")
    else:
        print(f"{file_path} does not exist.")
        data = fetch_all_archive_items()
        with open(file_path, 'w') as f:
            json.dump(data, f)
        print(f"\nSuccessfully fetched {len(data)} total issues.")
