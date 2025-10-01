import requests
import logging as log
from bs4 import BeautifulSoup


def get_soup(url) -> BeautifulSoup | None:
    """Fetches a URL and returns a BeautifulSoup object."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching {url}: {e}")
        return None
