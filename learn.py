import json
import time
from brain import MemoryDB, Avatar, Gateway, SILENT_MODE

LOOP_LEARNING = True  # <--- переключатель зацикливания обучения

avatar = Avatar()
memory = MemoryDB(debug=True, gpu_mode=True)
gateway = Gateway(memory_db=memory, avatar=avatar)

def check_system():
    print("Проверка системы при старте...")
    print(f"Текущий режим: SILENT_MODE = {SILENT_MODE}")
    print(f"Количество нейронов: {len(memory.neurons)}")
    print(f"Количество ассоциаций: {len(memory.associations)}")

time.sleep(1.5)
check_system()

try:
    with open("data/internal_dict.json", encoding="utf-8") as f:
        data = json.load(f)
        print(f"[LEARN] Данные загружены успешно.")

    phrases = [
        f"{entry.get('слово', '')} {entry.get('концепт', '')}".strip()
        for entry in data.values() if entry.get("слово")
    ]

    while True:
        for phrase in phrases:
            for word in phrase.split():
                gateway.memory.respond_and_express(word.strip(), used_in_output=True)
            time.sleep(0.01)
        if not LOOP_LEARNING:
            break

except Exception as e:
    print(f"[ERROR] Ошибка при обучении: {e}")

time.sleep(2)
memory.save_to_db()
print("Память сохранена вручную.")
