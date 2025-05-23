import time
from brain import MemoryDB, Avatar, Gateway, SILENT_MODE

# Инициализация аватара, памяти и шлюза
try:
    avatar = Avatar()
    memory = MemoryDB(debug=True)
    gateway = Gateway(memory_db=memory, avatar=avatar)
    print("🧠 Инициализация прошла успешно.")
except Exception as e:
    print(f"[ERROR] Ошибка при инициализации: {e}")
    exit()

# Пауза перед стартом
time.sleep(1.5)

def check_system():
    """Проверка системы при старте"""
    try:
        print("Проверка системы при старте...")
        print(f"Текущий режим: SILENT_MODE = {SILENT_MODE}")
        print(f"Количество нейронов: {len(memory.neurons)}")
        print(f"Количество ассоциаций: {len(memory.associations)}")
    except Exception as e:
        print(f"[ERROR] Ошибка при проверке системы: {e}")
        exit()

check_system()

def run_chat():
    """Запуск чат-сессии"""
    try:
        print("🔮 Живое существо ждёт твой сигнал. Напиши 'exit' чтобы выйти.\n")

        while True:
            # Ожидаем первый сигнал от пользователя
            text = input("👤 Ты: ").strip()

            if text.lower() in ("exit", "quit"):
                print("👋 До встречи.")
                break

            # Логируем полученное сообщение
            print(f"[CHAT] Получен сигнал: {text}")

            # Обрабатываем сигнал и генерируем ответ
            response = gateway.receive(text)

            # Печатаем ответ в консоль
            print(f"🧠 Ответ от системы: {response}")

            # Пауза, чтобы дать системе время для обработки и генерации
            time.sleep(1.5)

    except KeyboardInterrupt:
        print("\n🛑 Прервано пользователем.")
        exit()
    except Exception as e:
        print(f"[ERROR] Ошибка при обработке сигнала: {e}")
        print(f"[ERROR] Ошибка при обработке сигнала: {e}")  # Логируем ошибку

if __name__ == "__main__":
    try:
        print("🔮 Программа готова ожидать первого сигнала.")
        run_chat()
    except Exception as e:
        print(f"[ERROR] Ошибка при запуске чата: {e}")
