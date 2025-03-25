from playwright.sync_api import sync_playwright
import os

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
            content = page.content()

            # Сохраняем данные в файл
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Файл успешно сохранен в {save_path}")

            # Закрываем браузер
            browser.close()
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")

def main():
    url = "https://incpgameinfo.esportsworldlink.com/v2/odds?match_id=38141958"
    save_directory = r"C:\ELK\TestLogs"  # путь к папке
    save_path = os.path.join(save_directory, "log.json")  # имя файла

    # Создаем директорию, если она не существует
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Загружаем JSON
    download_json(url, save_path)

if __name__ == "__main__":
    main()