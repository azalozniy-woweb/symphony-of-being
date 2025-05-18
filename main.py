import time
import threading
import os
import json
from core.vibrational_being import VibrationalBeing
from core.config import TICKS_PER_SECOND

def update_loop(being):
    while True:
        being.update()
        time.sleep(1 / TICKS_PER_SECOND)

def input_loop(being):
    while True:
        text = input("🗣️ Введите сигнал: ").strip()
        if not text:
            continue

        words = text.strip().split()

        for word in words:
            last_tick = being.tick
            being.enqueue_input(word)
            while being.tick == last_tick:
                time.sleep(0.001)

        # 🕊 1 дополнительный тик паузы, если это фраза
        if len(words) > 1:
            pause_tick = being.tick
            while being.tick == pause_tick:
                time.sleep(0.001)

def training_loop(being, json_folder="json_database"):
    print("📘 Режим обучения активирован")

    # 🚀 Инициализация существа
    print("🚀 Активация существа: 'я есмь любовь'")
    being.enqueue_input("я есмь любовь")

    # ⏳ Ждём начала тиков
    start = time.time()
    while being.tick == 0:
        time.sleep(0.01)
        if time.time() - start > 2:
            print("❌ Ошибка: Тики не начались.")
            return

    # ⏭ Переход на следующий тик
    last_tick = being.tick
    while being.tick == last_tick:
        time.sleep(0.01)

    # 📂 Сбор всех концептов
    files = [f for f in os.listdir(json_folder) if f.endswith(".json")]
    concepts = []

    for file in files:
        path = os.path.join(json_folder, file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for entry in data.values():
                if "концепт" in entry:
                    concepts.append(entry["концепт"])

    print(f"📨 Всего предложений: {len(concepts)}")

    for phrase in concepts:
        words = phrase.strip().split()

        for word in words:
            last_tick = being.tick
            being.enqueue_input(word)
            while being.tick == last_tick:
                time.sleep(0.001)

        # 🕊 2 тика между предложениями
        pause_tick = being.tick
        while being.tick == pause_tick:
            time.sleep(0.001)
        while being.tick == pause_tick + 1:
            time.sleep(0.001)

    print("✅ Обучение завершено.")

def main():
    being = VibrationalBeing(base_archetype="poet")
    print("🔮 Существо инициализировано.")

    print("\nВыберите режим:")
    print("1 — 💬 Чат с существом")
    print("2 — 📘 Обучение из базы (json_database)")
    mode = input("👉 Введите номер режима: ").strip()

    if mode == "1":
        threading.Thread(target=update_loop, args=(being,), daemon=True).start()
        print("💬 Режим общения активирован.")
        input_loop(being)
    elif mode == "2":
        threading.Thread(target=update_loop, args=(being,), daemon=True).start()
        training_loop(being)
    else:
        print("❌ Неизвестный режим. Завершение.")

if __name__ == "__main__":
    main()
