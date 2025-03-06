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
        unique_match_ids = set()

        for match in data.get("result", []):
            for team in match.get("team", []):
                match_id = team.get("match_id")
                if match_id is not None:
                    unique_match_ids.add(match_id)

        if unique_match_ids:
            save_match_ids(unique_match_ids)
    else:
        print(f"Ошибка при запросе: {response.status_code}")

def save_match_ids(match_ids):
    try:
        with open("parsing_matches.txt", "r") as file:
            existing_ids = set(file.read().splitlines())
    except FileNotFoundError:
        existing_ids = set()
    
    new_ids = match_ids - existing_ids
    
    if new_ids:
        with open("parsing_matches.txt", "a") as file:
            for match_id in new_ids:
                file.write(f"{match_id}\n")
        print(f"Добавлены новые match_id: {new_ids}")
    else:
        print("Новых match_id нет.")

# Интервал обновления данных в секундах
update_interval = 10

while True:
    fetch_data()
    time.sleep(update_interval)