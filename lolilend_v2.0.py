import os, sys, time, json, re, requests
import ctypes

ACCESS_ID  = ""
TOKEN_FILE = "token.txt"
LOG_FILE   = "log.txt"

URL_REFRESH = "https://loliland.ru/apiv2/user/auth/token"
URL_BONUS   = "https://loliland.ru/apiv2/bonus/give"

def base():
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def path(f):
    return os.path.join(base(), f)

def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {msg}"
    try:
        with open(path(LOG_FILE), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def msgbox(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)

def headers(token):
    return {
        "accept":          "application/json",
        "accept-language": "ru",
        "content-type":    "application/json",
        "access-id":       ACCESS_ID,
        "access-token":    token,
        "origin":          "https://loliland.ru",
        "referer":         "https://loliland.ru/ru/cabinet/bonus",
        "user-agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/147.0.0.0 Safari/537.36 "
                           "OPR/131.0.0.0 (Edition std-2)",
    }

def load_token():
    p = path(TOKEN_FILE)
    if not os.path.exists(p):
        with open(p, "w") as f:
            f.write("ВСТАВЬТЕ_ТОКЕН_СЮДА")
        return None
    with open(p, "r") as f:
        t = f.read().strip()
    if not t or "ВСТАВЬТЕ" in t or len(t) < 20:
        return None
    return t

def save_token(t):
    with open(path(TOKEN_FILE), "w") as f:
        f.write(t)

def refresh(token):
    r = requests.post(URL_REFRESH,
                      json={"browser": "Opera GX", "system": "Windows 10"},
                      headers=headers(token),
                      timeout=15)
    if r.status_code == 200:
        new = r.json().get("accessToken")
        if new:
            return new
    return None

def bonus(token):
    r = requests.post(URL_BONUS, headers=headers(token), timeout=15)
    try:
        d = r.json()
    except:
        d = {}
    return r.status_code, d

def parse_wait_time(description: str) -> int:
    """
    Парсит строку вида:
    'До следующего получения бонуса должно пройти 22 часа 34 минуты 36 секунд'
    Возвращает время ожидания в секундах.
    """
    hours = 0
    minutes = 0
    seconds = 0

    # Ищем часы (час, часа, часов)
    h = re.search(r'(\d+)\s*час', description)
    if h:
        hours = int(h.group(1))

    # Ищем минуты (минута, минуты, минут)
    m = re.search(r'(\d+)\s*минут', description)
    if m:
        minutes = int(m.group(1))

    # Ищем секунды (секунда, секунды, секунд)
    s = re.search(r'(\d+)\s*секунд', description)
    if s:
        seconds = int(s.group(1))

    total = hours * 3600 + minutes * 60 + seconds

    # На случай если парсинг не сработал — ждём 1 час
    if total == 0:
        total = 3600

    # Добавляем 60 секунд запаса, чтобы не прийти на секунду раньше
    total += 60

    return total

def format_time(seconds: int) -> str:
    """Форматирует секунды в читаемый вид"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    parts = []
    if h > 0:
        parts.append(f"{h} ч")
    if m > 0:
        parts.append(f"{m} мин")
    if s > 0:
        parts.append(f"{s} сек")

    return " ".join(parts) if parts else "0 сек"

def main():
    log("=" * 50)
    log("LOLILAND AUTO-BONUS — запущен")
    log(f"Папка: {base()}")
    log("=" * 50)

    token = load_token()

    if not token:
        msgbox(
            "Loliland Auto-Bonus — Первый запуск",
            "Токен не найден!\n\n"
            "Как получить токен:\n"
            "1. Откройте loliland.ru в браузере\n"
            "2. Войдите в аккаунт\n"
            "3. Нажмите F12\n"
            "4. Перейдите во вкладку Console\n"
            "5. Введите: localStorage.access_token\n"
            "6. Скопируйте результат\n"
            "7. Вставьте в файл token.txt\n\n"
            f"Файл находится тут:\n{path(TOKEN_FILE)}\n\n"
            "После этого перезапустите программу."
        )
        log("Токен не найден. Программа завершена.")
        return

    log(f"Токен загружен: {token[:8]}...{token[-4:]}")

    attempt = 1
    while True:
        log(f"--- Попытка #{attempt} ---")

        try:
            # 1. Обновляем токен
            log("Обновление сессии...")
            new_token = refresh(token)

            if new_token:
                token = new_token
                save_token(token)
                log("Сессия продлена, токен сохранён.")
            else:
                log("❌ Не удалось обновить токен.")
                msgbox(
                    "Loliland Auto-Bonus — Ошибка",
                    "Токен устарел!\n\n"
                    "Обновите token.txt:\n"
                    "1. Зайдите на loliland.ru\n"
                    "2. F12 → Console\n"
                    "3. Введите: localStorage.access_token\n"
                    "4. Вставьте в token.txt\n\n"
                    f"Путь к файлу:\n{path(TOKEN_FILE)}"
                )
                wait = 3600
                log(f"Ожидание {format_time(wait)}...")
                time.sleep(wait)
                token = load_token() or token
                attempt += 1
                continue

            # 2. Забираем бонус
            log("Запрос бонуса...")
            code, data = bonus(token)

            if code == 200:
                log("🎉 БОНУС ПОЛУЧЕН!")
                log(json.dumps(data, ensure_ascii=False, indent=2))
                # После успеха ждём 23 часа
                wait = 23 * 3600
                log(f"Следующая попытка через {format_time(wait)}")
                time.sleep(wait)
                attempt = 1
                continue

            elif data.get("error_code") == -9:
                desc = data.get("details", {}).get("description", "")
                log(f"⏳ {desc}")

                # Парсим точное время ожидания из ответа сервера
                wait = parse_wait_time(desc)
                log(f"Следующая попытка через {format_time(wait)}")
                time.sleep(wait)

            elif code == 401:
                log("⚠️ Токен не принят для бонуса.")
                wait = 3600
                log(f"Ожидание {format_time(wait)}...")
                time.sleep(wait)

            else:
                log(f"⚠️ Ответ: {json.dumps(data, ensure_ascii=False)}")
                wait = 3600
                log(f"Ожидание {format_time(wait)}...")
                time.sleep(wait)

        except requests.ConnectionError:
            log("⚠️ Нет интернета. Повтор через 5 мин.")
            time.sleep(300)
        except requests.Timeout:
            log("⚠️ Сервер не отвечает. Повтор через 5 мин.")
            time.sleep(300)
        except Exception as e:
            log(f"❌ Ошибка: {e}")
            time.sleep(3600)

        attempt += 1

if __name__ == "__main__":
    main()
