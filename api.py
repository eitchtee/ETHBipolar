import requests


def get_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=brl,usd&include_24hr_change=true"

    response = requests.request("get", url)
    json = response.json()
    brl_valor = json['ethereum']['brl']
    usd_valor = json['ethereum']['usd']
    brl_24h = json['ethereum']['brl_24h_change']
    usd_24hr = json['ethereum']['usd_24h_change']

    brl_24h = "{:+,.2%}".format(brl_24h).replace('.', ',')
    usd_24hr = "{:+,.2%}".format(usd_24hr).replace('.', ',')

    return brl_valor, brl_24h, usd_valor, usd_24hr
