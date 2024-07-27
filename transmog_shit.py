import requests


def shorten_url(long_url):
    """Shorten a URL using a service like TinyURL."""
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={long_url}")
        return response.text if response.status_code == 200 else long_url
    except:
        return long_url
