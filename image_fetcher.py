from requests import get, models


def get_from_bing(query: str) -> models.Response:
    binq_url = "https://th.bing.com/th?q="

    res = get(binq_url + query)
    if res:
        return res.content

    print("fetching error")
    return None
