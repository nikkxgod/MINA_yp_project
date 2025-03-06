import requests
import time

# Настройки прокси
proxy_ip = "138.36.139.160"
proxy_port = "8000"
proxy_login = "bs40JB"
proxy_password = "uFsRwH"

proxy_url = f"http://{proxy_login}:{proxy_password}@{proxy_ip}:{proxy_port}"

# URL API
url = "https://incpgameinfo.esportsworldlink.com/v2/match?match_type=2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

proxies = {
    "http": proxy_url,
    "https": proxy_url,
}

def fetch_data():
    response = requests.get(url, headers=headers, proxies=proxies)

    if response.status_code == 200:
        data = response.json()