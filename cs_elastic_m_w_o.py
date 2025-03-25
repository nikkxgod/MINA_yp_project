import cloudscraper
import json
from elasticsearch import Elasticsearch
import time
from datetime import datetime, UTC
import os


def clean_document(data):
    dict = {
        'game_id': data['result'].get('game_id'),
        'game_name': data['result'].get('game_name'),
        'tournament_short_name': data['result'].get('tournament_short_name'),
        'match_id': data['result'].get('id'),
        'match_name': data['result'].get('match_short_name'),
        'round': data['result'].get('round'),
        'start_time': data['result'].get('start_time'),
        'end_time': data['result'].get('end_time'),
        'status': data['result'].get('status'),
        'teams': [],
        'odds': [
            {
                'update_time': datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                'odds': [odd for odd in {'odds': data['result']['odds']}['odds'] if odd.get('group_short_name') == 'Winner']
            }
        ]
    }

    teams = data['result'].get('team', [])
    for team in teams:
        team_data = {
            'team_id': team.get('team_id'),
            'team_name': team.get('team_short_name'),
            'pos': team.get('pos'),
            'score': {
                'r1': team.get('score', {}).get('r1'),
                'r2': team.get('score', {}).get('r2'),
                'r3': team.get('score', {}).get('r3'),
                'total': team.get('score', {}).get('total')
            }
        }
        dict['teams'].append(team_data)

    return dict


def get_json(url):
    try:

        response = scraper.get(url, proxies=proxies)

        if response.status_code == 200:
            print(f"Исходный файл c матчем успешно получен")
            return json.loads(response.text)
        else:
            print(f"Ошибка: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при получении файла: {e}")
        if 'response' in locals():
            print(f"Ответ сервера: {response.text}")
        return None


def upload_to_elasticsearch(data, index_name):
    try:
        if not es.ping():
            print("Ошибка подключения к Elasticsearch")
            return

        es.index(index=index_name, id=data.get("match_id"), document=data)
        print(f"Документ успешно загружен в индекс {index_name}")
    except Exception as e:
        print(f"Ошибка при загрузке данных в Elasticsearch: {e}")


def update_odds(data):
    match_id = data['match_id']
    doc = es.get(index="matches_w_odds", id=match_id)
    source = doc["_source"]

    if "odds" in source:
        source["odds"].append(data['odds'][0])
    else:
        source["odds"] = [data['odds'][0]]

    es.index(index="matches_w_odds", id=match_id, document=source)
    print(f"Документ {match_id} успешно обновлен.")


if __name__ == "__main__":
    try:
        es = Elasticsearch(
            hosts=["https://localhost:9200"],
            basic_auth=("elastic", "123456"),
            verify_certs=False
        )
    except Exception as e:
        print(f"Ошибка при подключении к Elasticsearch: {e}")

    proxy_username = "bs40JB"
    proxy_password = "uFsRwH"
    proxy_host = "138.36.139.160"
    proxy_port = "8000"

    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://example.com/",
    }

    scraper = cloudscraper.create_scraper()

    save_directory = r"C:\ELK\TestLogs"
    save_path = os.path.join(save_directory, "log.json")

    set_of_ids = set()
    time_for_update_ids = 60

    while True:
        if time_for_update_ids == 60:
            get_ids_url = "https://incpgameinfo.esportsworldlink.com/v2/match?match_type=2"
            session = cloudscraper.create_scraper()
            response = session.get(get_ids_url, proxies=proxies, headers=headers)

            if response.status_code == 200:
                ids = response.json()
                time_for_update_ids = 0
                for match in ids.get("result", []):
                    for team in match.get("team", []):
                        match_id = team.get("match_id")
                        if match_id is not None:
                            set_of_ids.add(match_id)
                print(f"Исходный файл c ids успешно получен")
            else:
                print(f"Ошибка в получении ids: {response.status_code}")
                set_of_ids = set()

            time.sleep(5)

        print(set_of_ids)
        for id in set_of_ids:
            url = f"https://incpgameinfo.esportsworldlink.com/v2/odds?match_id={id}"

            data = get_json(url)
            if data:
                cleaned_data = clean_document(data)
                with open(save_path, "w", encoding="utf-8") as file:
                    json.dump(cleaned_data, file, indent=4, ensure_ascii=False)
                if es.exists(index="matches_w_odds", id=cleaned_data['match_id']):
                    update_odds(cleaned_data)
                else:
                    upload_to_elasticsearch(cleaned_data, "matches_w_odds")

        time_for_update_ids += 1

