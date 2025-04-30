import os
from typing import Optional, Tuple

from icrawler.builtin import GoogleImageCrawler


class MedicineBoxImageCrawler:
    def __init__(self, base_dir: str) -> None:
        """
        Initializes the crawler with a base directory where images will be saved.

        Args:
            base_dir (str): Path to the directory to save downloaded images.
        """
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def fetch_data(
        self,
        keyword: str,
        max_num: int = 100,
        min_size: Tuple[int, int] = (200, 200),
        max_size: Optional[Tuple[int, int]] = None,
    ) -> None:
        """
        Downloads images from Google Images using icrawler based on the provided keyword.

        Args:
            keyword (str): Search term for images (e.g., "medicine box").
            max_num (int): Maximum number of images to download.
            min_size (Tuple[int, int]): Minimum size (width, height) of images to download.
            max_size (Optional[Tuple[int, int]]): Maximum size (width, height) of images to download.
        """
        crawler = GoogleImageCrawler(storage={"root_dir": self.base_dir})
        crawler.crawl(
            keyword=keyword, max_num=max_num, min_size=min_size, max_size=max_size
        )
