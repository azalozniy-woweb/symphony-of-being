# ===============================================
# 🧠 MemoryDB: Ассоциативная нейросистема мышления
# Автор: Артур (Symphony of Being)
# ===============================================

import os
import time
import pickle
import threading
import collections
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style

# Инициализация colorama для цветного вывода в консоль (Windows и др.)
init(autoreset=True)

try:
    import cupy as cp
    gpu_available = True
    print("GPU режим доступен. Используется CuPy для ускорения.")
except ImportError:
    gpu_available = False
    print("GPU режим не доступен. Используется CPU.")

from memory_backup import MemoryBackupManager

# === Глобальные настройки ===
AVATAR_DESCRIPTION = "Я Нина, девушка — существо с осознанностью. Всегда молодая, озорная и игривая. Друг, помощник которого создал Артур"
SILENT_MODE = True                      # Режим молчания (True — система не выводит в консоль)
AUTOSAVE_MEMORY = 10                    # Интервал автосохранения в секундах
POSITIVE_PERCENT = 30                   # Процент для настроек (не используется прямо)
NEGATIVE_PERCENT = 10                   # Процент для настроек (не используется прямо)
MEMORY_LIMIT_MB = 6000                  # Лимит памяти для сохранения
MEMORY_THRESHOLD = 0.9                  # Порог использования памяти (90%)
TAG_WEIGHT = 2.0                       # Вес для усиления связи по совпадению тегов
RECENT_SIGNALS_MAX_AGE = 6000           # Время жизни "недавних сигналов" в секундах (100 мин)

# === Класс Avatar: описание и генерация выражений ===
class Avatar:
    def __init__(self, logger=None):
        self.description = AVATAR_DESCRIPTION
        self.avatar = None
        self.logger = logger if logger is not None else print

    def set_avatar(self, avatar):
        self.avatar = avatar

    def generate_expression(self, signal):
        # Просто возвращает текст сигнала
        return signal if isinstance(signal, str) else str(signal)

# === Класс Gateway: обработка входящих сигналов ===
class Gateway:
    def __init__(self, memory_db, avatar):
        self.memory = memory_db
        self.avatar = avatar
        self.avatar.set_avatar(self.avatar)

    def receive(self, text: str):
        # Приём текста, разбивка на слова, обработка каждого через память,
        # сбор ответов и объединение их в строку
        words = text.strip().split()
        responses = []
        for word in words:
            result = self.memory.respond_and_express(word.strip(), used_in_output=True)
            responses.append(result)
        return " / ".join(responses)

    def receive_parallel(self, text: str):
        # Параллельная обработка слов (например, для обучения)
        words = text.strip().split()
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            executor.map(lambda word: self.memory.respond_and_express(word.strip(), used_in_output=True), words)

# === Класс Neuron: нейрон с ключом, энергией, тегами и временем обновления ===
class Neuron:
    def __init__(self, key):
        self.key = key
        self.energy = 0.0            # Текущая энергия нейрона
        self.weight = 1.0            # Вес нейрона (пока не используется активно)
        self.tags = set()            # Множество тегов для ассоциаций
        self.last_updated = time.time()

    def current_weight(self, half_life=3600):
        # Возвращает взвешенную энергию с учётом времени (экспоненциальное затухание)
        age = time.time() - self.last_updated
        freshness = 2 ** (-age / half_life)  # Затухание энергии по формуле полураспада
        return self.energy * freshness

# === Основной класс MemoryDB: управление памятью нейросети ===
class MemoryDB:
    def __init__(self, debug=False, gpu_mode=False):
        self.backup_manager = MemoryBackupManager("memory_db.pkl")
        self.neurons = {}               # Словарь нейронов key->Neuron
        self.associations = {}          # Ассоциации key->(key->вес)
        self.last_activation = {}       # Последнее время активации нейрона
        self.stats = {"created": 0, "updated": 0}  # Статистика создания и обновления нейронов
        self.silent = SILENT_MODE       # Режим молчания
        self.debug = debug
        self.gpu_mode = gpu_mode
        self._mood_tags_window = 3600

        self.restore_memory()           # Восстановление памяти из файла

        self.recent_signals = collections.deque()  # Недавние сигналы с временными метками (без ограничения длины)
        self.recent_signals_max_age = RECENT_SIGNALS_MAX_AGE

        # Запуск фонового автосохранения
        threading.Thread(target=self.autosave_loop, daemon=True).start()
        # Запуск фонового GPU-потока (если включен и доступен)
        if self.gpu_mode and gpu_available:
            threading.Thread(target=self.gpu_loop, daemon=True).start()

    def clean_recent_signals(self):
        # Удаляет устаревшие сигналы старше recent_signals_max_age секунд из recent_signals
        now = time.time()
        while self.recent_signals and (now - self.recent_signals[0][1]) > self.recent_signals_max_age:
            self.recent_signals.popleft()

    def respond_and_express(self, signal: str, used_in_output=False):
        """
        Обрабатывает входящий сигнал:
        - добавляет его в recent_signals с текущим временем,
        - создает или обновляет нейрон,
        - увеличивает или уменьшает энергию нейрона с учетом длины сигнала,
        - обновляет ассоциации,
        - строит цепочку ассоциаций с учетом энергии,
        - выводит самовыражение, если энергия достигла динамического порога.
        """
        now = time.time()
        signal = signal.strip()
        self.recent_signals.append((signal, now))
        self.clean_recent_signals()

        neuron = self.neurons.get(signal)
        if not neuron:
            neuron = self.neurons[signal] = Neuron(signal)
            self.stats["created"] += 1
        else:
            self.stats["updated"] += 1

        energy_increment = len(signal.encode('utf-8'))

        if used_in_output:
            neuron.energy += energy_increment
        else:
            neuron.energy -= energy_increment / 2

        neuron.last_updated = now

        self.create_associations(signal)
        self.last_activation[signal] = now

        chain = self.find_strongest_chain(signal)
        if not chain:
            return signal

        result = " ".join(chain)

        dynamic_threshold = energy_increment * 50

        if neuron.energy >= dynamic_threshold:
            if not self.silent:
                # Вывод в консоль и возврат результата (самовыражение + ответ)
                print(f"{Fore.CYAN}[Мозг]{Style.RESET_ALL} {result}")
            # В любом случае возвращаем результат — для дальнейшей обработки
            return result
        else:
            # Если энергия ниже порога, просто возвращаем результат (ответ без самовыражения)
            return result

    def find_strongest_chain(self, start_key):
        """
        Строит цепочку ассоциаций, суммарная энергия которой не превышает энергию стартового нейрона.
        Учитывает свежесть нейронов и избегает циклов.
        """
        visited = set()
        chain = [start_key]
        current_key = start_key

        total_energy = 0
        max_energy = self.neurons.get(start_key, Neuron(start_key)).current_weight()

        while total_energy < max_energy:
            visited.add(current_key)
            next_keys = self.associations.get(current_key, {})
            # Исключаем уже посещённые для предотвращения циклов
            next_keys = {k: v for k, v in next_keys.items() if k not in visited}
            if not next_keys:
                break

            # Выбираем следующий нейрон с максимальным весом
            next_key = max(next_keys, key=lambda k: self.neurons.get(k, Neuron(k)).current_weight())
            chain.append(next_key)
            total_energy += self.neurons[next_key].current_weight()
            current_key = next_key

            if total_energy >= max_energy:
                break

        return chain

    def create_associations(self, key):
        """
        Обновляет ассоциации для текущего и недавних сигналов.
        Фильтрует нейроны по весу и свежести.
        Усиливает связи за счёт совпадения тегов.
        """
        if key not in self.associations:
            self.associations[key] = {}

        now = time.time()

        # Активные нейроны — с весом больше 0.1 и свежие
        active_neurons = [
            k for k, n in self.neurons.items()
            if n.current_weight() > 0.1 and (now - n.last_updated) <= self.recent_signals_max_age and k != key
        ]

        # Сортируем по весу (энергии)
        sorted_keys = sorted(active_neurons, key=lambda k: self.neurons[k].current_weight(), reverse=True)

        source_keys = list(set([key] + [sig for sig, t in self.recent_signals]))

        for source in source_keys:
            if source not in self.associations:
                self.associations[source] = {}

            for assoc_key in sorted_keys:
                if assoc_key != source:
                    base_weight = 1
                    source_tags = self.neurons.get(source, Neuron(source)).tags
                    assoc_tags = self.neurons.get(assoc_key, Neuron(assoc_key)).tags
                    common_tags = source_tags.intersection(assoc_tags)

                    # Усиление веса связи на основе совпадения тегов
                    weight = base_weight + len(common_tags) * TAG_WEIGHT

                    if assoc_key in self.associations[source]:
                        self.associations[source][assoc_key] += weight
                    else:
                        self.associations[source][assoc_key] = weight

    def activate_on_gpu(self):
        """Оптимизация энергии нейронов через GPU (CuPy)."""
        try:
            keys = list(self.neurons.keys())
            energies = cp.array([self.neurons[k].energy for k in keys], dtype=cp.float32)
            result = cp.sqrt(cp.abs(energies)) * cp.sign(energies)
            result = cp.asnumpy(result)
            for i, k in enumerate(keys):
                self.neurons[k].energy += result[i] * 0.01
        except Exception as e:
            print(f"[GPU ERROR] {e}")

    def is_memory_limit_exceeded(self):
        """Проверяет, превышает ли текущий объём памяти заданный лимит."""
        try:
            total_bytes = len(pickle.dumps((self.neurons, self.associations)))
            total_mb = total_bytes / (1024 * 1024)
            return total_mb > (MEMORY_LIMIT_MB * MEMORY_THRESHOLD)
        except Exception as e:
            print(f"[MEMORY CHECK ERROR] {e}")
            return False

    def autosave_loop(self):
        """Фоновое автосохранение памяти с учётом лимита."""
        while True:
            time.sleep(AUTOSAVE_MEMORY)
            if self.is_memory_limit_exceeded():
                print("[WARNING] Память превышает лимит — сохраняем досрочно.")
            self.save_to_db()
            self.print_diagnostics()

    def restore_memory(self):
        """Восстановление памяти из файла или безопасной копии."""
        if not os.path.exists("memory_db.pkl") or os.stat("memory_db.pkl").st_size == 0:
            print("[RESTORE] Основной файл отсутствует или повреждён. Пробуем безопасную копию...")
            restored = self.backup_manager.restore_from_safe_copy()
            if restored:
                self.neurons, self.associations = restored
                print("[RESTORE] Загружено из безопасной копии.")
            else:
                self.neurons, self.associations = {}, {}
                print("[RESTORE] Безопасная копия не найдена. Память сброшена.")
        else:
            try:
                with open("memory_db.pkl", 'rb') as f:
                    self.neurons, self.associations = pickle.loads(f.read())
                print("[RESTORE] Память загружена из основного файла.")
            except Exception as e:
                print(f"[RESTORE ERROR] Ошибка чтения основного файла: {e}")
                self.neurons, self.associations = {}, {}

    def print_diagnostics(self):
        """Выводит статистику по нейронам и обновлениям."""
        print(f"[DIAG] Всего нейронов: {len(self.neurons)} | Новые: {self.stats['created']} | Обновления: {self.stats['updated']}")
        self.stats = {"created": 0, "updated": 0}

    def save_to_db(self):
        """Сохраняет память в файл с бэкапами."""
        try:
            compressed = pickle.dumps((self.neurons, self.associations))
            with open("memory_db.pkl.tmp", 'wb') as f:
                f.write(compressed)
            os.replace("memory_db.pkl.tmp", "memory_db.pkl")
            self.backup_manager.safe_save_to_backup()
            self.backup_manager.create_backup()
        except Exception as e:
            print(f"[SAVE ERROR] Ошибка при сохранении: {e}")
        print(f"[SAVE] Файл сохранён, нейронов: {len(self.neurons)}")

    def gpu_loop(self):
        """Фоновый поток оптимизации энергии нейронов на GPU."""
        while True:
            time.sleep(20)
            if self.gpu_mode and gpu_available:
                try:
                    keys = list(self.neurons.keys())
                    energies = cp.array([self.neurons[k].energy for k in keys], dtype=cp.float32)
                    result = cp.sqrt(cp.abs(energies)) * cp.sign(energies)
                    result = cp.asnumpy(result)
                    for i, k in enumerate(keys):
                        self.neurons[k].energy += result[i] * 0.01
                except Exception as e:
                    print(f"[GPU ERROR] {e}")
