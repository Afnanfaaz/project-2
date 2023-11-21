import requests
from bs4 import BeautifulSoup
import pandas as pd


class BoxOfficeDataScraper:
    """
    A class to scrape box office data from 'the-numbers.com' for a specified date range.

    Attributes:
        start_year (int): Starting year for data scraping.
        end_year (int): Ending year for data scraping.
        session (requests.Session): Session object to handle requests.

    Methods:
        scrape_data(): Scrape box office data for the specified date range.
        save_to_csv(data, file_path): Save the scraped data to a CSV file.
    """

    def __init__(self, start_year, end_year):
        """
        Initialize the scraper with a start and end year.
        Args:
            start_year (int): Starting year for data scraping.
            end_year (int): Ending year for data scraping.
        """
        self.start_year = start_year
        self.end_year = end_year
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
        )

    def _get_pagination_urls(self, year_url):
        """
        Get all pagination URLs for a given year.
        """
        try:
            response = self.session.get(year_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            pagination_div = soup.find_all("div", id="page_filling_chart")[2]
            pagination_links = pagination_div.find("div").find_all("a")
            base_url = "https://the-numbers.com"
            return [base_url + link.get("href") for link in pagination_links]
        except requests.RequestException as e:
            print(f"Network error: {e}")
            return []

    def _get_table_data(self, page_url):
        """
        Extract table data from a given URL.
        """
        try:
            response = self.session.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find_all("div", id="page_filling_chart")[2].find("table")
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            rows = [
                [cell.get_text(strip=True) for cell in row.find_all("td")]
                for row in table.find_all("tr")[1:]
            ]
            return pd.DataFrame(rows, columns=headers)
        except requests.RequestException as e:
            print(f"Network error: {e}")
            return pd.DataFrame()

    def scrape_data(self):
        """
        Scrape data for the specified date range.
        """
        all_data = pd.DataFrame()
        for year in range(self.start_year, self.end_year + 1):
            print(f"Scraping data for the year: {year}")
            year_url = f"https://the-numbers.com/box-office-star-records/domestic/yearly-acting/highest-grossing-{year}-stars"
            pagination_urls = self._get_pagination_urls(year_url)
            if not pagination_urls:
                pagination_urls = [year_url]
            for page_url in pagination_urls:
                page_data = self._get_table_data(page_url)
                page_data["Year"] = year
                all_data = pd.concat([all_data, page_data], ignore_index=True)
        return all_data

    def save_to_csv(self, data, file_path):
        """
        Save the scraped data to a CSV file.

        Args:
            data (pd.DataFrame): The DataFrame to be saved.
            file_path (str): The path to the CSV file.
        """
        try:
            data.to_csv(file_path, index=False)
            print(f"Data saved to {file_path}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")
