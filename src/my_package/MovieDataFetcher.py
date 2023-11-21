import requests
import pandas as pd


class FilmDataCollector:
    """
    A class to fetch top-rated movie data from The Movie Database API.

    Attributes:
        access_key (str): API key for authentication.
        api_endpoint (str): Base URL for the top-rated movies endpoint.
        movie_data (pd.DataFrame): DataFrame to store fetched movie data.

    Methods:
        fetch_movie_data(pages): Fetches movie data over a specified number of pages.
        send_request(page): Sends a GET request to the API for a specific page.
        process_api_response(response): Processes the JSON response from the API.
        add_data(data): Appends new data to the movie_data DataFrame.
        retrieve_dataframe(): Returns the movie_data DataFrame.
    """

    def __init__(self, api_key):
        self.access_key = api_key
        self.api_endpoint = "https://api.themoviedb.org/3/movie/top_rated"
        self.movie_data = pd.DataFrame()

    def fetch_movie_data(self, pages=1):
        for i in range(1, pages + 1):
            response = self.send_request(i)
            if response and response.status_code == 200:
                data = self.process_api_response(response)
                self.add_data(data)
            else:
                print(f"Data fetch error for page {i}: Status {response.status_code}")

    def send_request(self, page_number):
        try:
            url = f"{self.api_endpoint}?api_key={self.access_key}&language=en-US&page={page_number}"
            response = requests.get(url)
            return response
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def process_api_response(self, response):
        temp_df = pd.DataFrame(response.json()["results"])
        columns = [
            "id",
            "title",
            "overview",
            "release_date",
            "popularity",
            "vote_average",
            "vote_count",
        ]
        return temp_df[columns]

    def add_data(self, data):
        self.movie_data = pd.concat([self.movie_data, data], ignore_index=True)

    def retrieve_dataframe(self):
        return self.movie_data
