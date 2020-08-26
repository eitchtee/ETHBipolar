import requests


def get_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=brl,usd"

    response = requests.request("get", url)
    json = response.json()
    return json['ethereum']['brl'], json['ethereum']['usd']
