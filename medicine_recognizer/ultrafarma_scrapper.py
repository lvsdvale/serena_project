""""This file implements scrapper for medicine box images in ultrafarma website"""

import os
from urllib.parse import quote
from urllib.request import urlretrieve

import requests
from bs4 import BeautifulSoup


class UltrafarmaScraper:
    """
    A scraper that collects product images from Ultrafarma's website.
    Useful for building image datasets.
    """

    def __init__(self, base_dir="medicine_database"):
        """
        Initializes the scraper with a base directory to store images.

        parameters:
            base_dir (str): Root folder where search folders will be created.
        """
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def fetch_images(self, search_term):
        """
        Fetches product images for a given search term from Ultrafarma,
        and saves them inside a dedicated folder.

        parameters:
            search_term (str): Medicine name or search keyword.

        Returns:
            int: Number of images successfully downloaded.
        """

        target_folder = os.path.join(self.base_dir, search_term)
        os.makedirs(target_folder, exist_ok=True)

        encoded_term = quote(search_term)
        search_url = f"https://www.ultrafarma.com.br/busca?q={encoded_term}"

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)

        if response.status_code != 200:
            print(
                f"[✗] Failed to access {search_url} - Status code: {response.status_code}"
            )
            return 0

        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("div", class_="product-item")

        print(f"[→] Found {len(products)} products for '{search_term}'.")

        image_count = 0
        for product in products:
            img_tag = product.find("img")
            if img_tag and img_tag.get("src"):
                image_url = img_tag["src"]
                print(f"[→] Found image URL: {image_url}")  # Debugging line
                filename = os.path.join(
                    target_folder, f"{search_term}_{image_count}.jpg"
                )
                try:
                    urlretrieve(image_url, filename)
                    print(f"[✓] Image saved: {filename}")
                    image_count += 1
                except Exception as e:
                    print(f"[✗] Failed to download image: {e}")
            else:
                print("[!] No img tag or src attribute found.")  # Debugging line

        if image_count == 0:
            print("[!] No images were downloaded.")

        return image_count
