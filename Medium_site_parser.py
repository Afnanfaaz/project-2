import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


class ArticleSitemapParser:
    """
    Extracts and organizes sitemap URLs from a website, specifically for article listings.

    Attributes:
        main_url (str): Base URL of the website for scraping.
        url_maps (dict): Dictionary storing URLs from sitemaps and their respective dataframes.
        sitemap_count (int): Counter for the number of sitemaps processed.
        max_sitemaps (int): Maximum number of sitemaps to process.

    Methods:
        retrieve_webpage(url): Retrieves content from a specified URL.
        analyze_sitemap(url_of_sitemap): Analyzes a sitemap URL, extracting all URLs.
        compile_sitemaps(): Compiles sitemaps from the site's robots.txt.
        process_urls(): Processes and extracts subdirectories from each URL.
        export_to_csv(folder_path): Exports sitemap data to CSV files in a given folder.
    """

    def __init__(self, main_url):
        """
        Sets up the ArticleSitemapParser with a website URL.
        Parameters:
            main_url (str): Base URL of the website for scraping.
        """
        self.main_url = main_url
        self.url_maps = {}
        self.sitemap_count = 0
        self.max_sitemaps = 30
        self.compile_sitemaps()

    def retrieve_webpage(self, url):
        """
        Retrieves content from a URL using HTTP GET with headers.
        Parameters:
            url (str): URL to retrieve content from.
        Returns:
            str: Webpage content or an empty string if error.
        """
        try:
            head_info = {"User-Agent": "Mozilla/5.0"}
            web_response = requests.get(url, headers=head_info)
            web_response.raise_for_status()
            return web_response.text
        except requests.RequestException as err:
            return ""

    def analyze_sitemap(self, url_of_sitemap):
        """
        Analyzes and stores URLs from a sitemap, handles nested sitemaps.
        Stops if the number of processed sitemaps reaches the maximum limit.
        Parameters:
            url_of_sitemap (str): Sitemap URL to analyze.
        """
        if self.sitemap_count >= self.max_sitemaps:
            return

        sitemap_content = self.retrieve_webpage(url_of_sitemap)
        bs_parser = BeautifulSoup(sitemap_content, "xml")
        found_urls = []

        for location in bs_parser.find_all("loc"):
            found_url = location.get_text()
            found_urls.append(found_url)
            if found_url.endswith(".xml") and self.sitemap_count < self.max_sitemaps:
                self.sitemap_count += 1
                self.analyze_sitemap(found_url)

        self.url_maps[url_of_sitemap] = pd.DataFrame(found_urls, columns=["URLs"])

    def compile_sitemaps(self):
        """
        Retrieves and processes sitemaps from the site's robots.txt.
        """
        robots_content = self.retrieve_webpage(f"{self.main_url}/robots.txt")
        for line in robots_content.splitlines():
            if line.startswith("Sitemap:"):
                sitemap_url = line.split(": ")[1].strip()
                if self.sitemap_count < self.max_sitemaps:
                    self.sitemap_count += 1
                    self.analyze_sitemap(sitemap_url)

    def process_urls(self):
        """
        Processes URLs, extracting subdirectories.
        """
        for map_key, data_frame in self.url_maps.items():
            data_frame["Subdirs"] = data_frame["URLs"].apply(
                lambda x: x.replace("https://medium.com/", "").split("/")
            )

    def export_to_csv(self, folder_path="extracted_sitemaps"):
        """
        Exports dataframes to CSV in a specified folder.
        Parameters:
            folder_path (str): Folder to save CSV files.
        """
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for map_name, data_frame in self.url_maps.items():
            csv_filename = f"{folder_path}/{map_name.split('/')[-1]}.csv"
            data_frame.to_csv(csv_filename, index=False)
