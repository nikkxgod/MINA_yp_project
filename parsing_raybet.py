from playwright.sync_api import sync_playwright
import os
import json
from datetime import datetime, timedelta
import time
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

def parsing_ids():
    fetch_data()

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
    # Очищаем файл перед записью новых матчей
    with open("parsing_matches.txt", "w") as file:
        for match_id in match_ids:
            file.write(f"{match_id}\n")

    print(f"Сохранены новые match_id: {match_ids}")




def download_json(url, save_path):
    try:
        # Запуск Playwright
        with sync_playwright() as p:
            # Запуск браузера (можно использовать chromium, firefox или webkit)
            browser = p.chromium.launch(headless=True, proxy={
                "server": "http://138.36.139.160:8000",
                "username": "bs40JB",
                "password": "uFsRwH"
            })  # headless=True для фонового режима
            page = browser.new_page()

            # Переход на страницу
            page.goto(url)

            # Ожидание загрузки данных (можно настроить под конкретный сайт)
            page.wait_for_selector("body")  # Ждем, пока загрузится body

            # Получаем содержимое страницы
            content = page.evaluate("() => document.body.innerText")
            browser.close()
            data = json.loads(content)
            if data['result']['status'] == '3':


                # добавить запись резултатов из поля score потом


                start()
            now = datetime.now()
            start_time = (datetime.strptime(data['result']['start_time'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
            map1 = {}
            map2 = {}
            status=['','prematch','live','end']
            status_code = data['result']['status']
            if data['result']['game_name']=='CS2':
                for i in data['result']['odds']:
                    if i['match_stage']=='map1' and i['odds_group_id']==16854:
                        map1[i['name']]=i['odds']
                    if i['match_stage']=='map2' and i['odds_group_id']==16877:
                        map2[i['name']]=i['odds']
            else:
                return
            # elif data['result']['game_name']=='无尽对决':
            #     for i in data['result']['odds']:
            #         if i['match_stage']=='r1' and i['sort_index']==2879800:
            #             map1[i['name']]=i['odds']
            #         if i['match_stage']=='r2' and i['sort_index']==2878950:
            #             map2[i['name']]=i['odds']
            dict = {
                '_id': data['result']['id'], 
                'game_name': data['result']['game_name'],
                'match_name': data['result']['match_name'],
                'tournament_short_name': data['result']['tournament_short_name'],
                'start_time': start_time,
                'status':status[status_code],
                'round':data['result']['round'],
                'teams':[data['result']['team'][0]['team_name'],data['result']['team'][1]['team_name']],
                'odds':[{
                        'Date time': f'{now.strftime("%d/%m/%Y %H:%M:%S")}',
                        'Winner': {
                            data['result']['odds'][0]['name']: data['result']['odds'][0]['odds'],
                            data['result']['odds'][1]['name']: data['result']['odds'][1]['odds']
                        },
                        'Map 1': map1,
                        'Map 2': map2
                }]
                }
            
            # Сохраняем данные в файл в формате JSON
            with open(save_path, 'w', encoding='utf-8') as file:
                json.dump(dict, file, ensure_ascii=False, indent=4)  # Записываем словарь в JSON    

    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")

def main(match_id):
    url = f"https://incpgameinfo.esportsworldlink.com/v2/odds?match_id={match_id}"
    save_directory = r"C:\ELK\TestLogs"  # путь к папке
    save_path = f"log{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"  # имя файла

    # Создаем директорию, если она не существует
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    # Загружаем JSON
    download_json(url, save_path)

def read_file_to_array(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = [line.strip() for line in file if line.strip()]
        return data
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return []


filename = "parsing_matches.txt"

def start():
    parsing_ids()
    parsing_matches()

def parsing_matches():
    while True:
       matches = read_file_to_array(filename)
       for match in matches:
           main(match)
       time.sleep(5)

if __name__ == "__main__":
    start()