from bs4 import BeautifulSoup
import requests


def extract_from_url(url: str) -> str:
    """Extract text content from URL using BeautifulSoup"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return " ".join(p.get_text() for p in soup.find_all("p"))
