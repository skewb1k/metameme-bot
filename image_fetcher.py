from requests import get


def fetch_image_by_query(query: str):
    binq_url = "https://th.bing.com/th?q="
    print("query", query)

    res = get(binq_url + query)
    if res:
        print(type(res))
        return res.content

    print("fetching error")
    return None
