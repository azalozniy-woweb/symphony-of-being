import random
import os
import pickle
import time
import sys
import psutil
from core.config import (
    BRAIN_SAVE_PATH,
    BRAIN_MAX_RAM_MB,
    BRAIN_MAX_RAM_PERCENT,
    BRAIN_AUTO_SAVE_INTERVAL,
    TICKS_PER_SECOND
)
from core.config import FALLBACK_EMOTIONS
from core.logger import trace_method

class Brain:
    def __init__(
            self,
            save_path=BRAIN_SAVE_PATH,
            max_ram_mb=BRAIN_MAX_RAM_MB,
            max_ram_percent=BRAIN_MAX_RAM_PERCENT,
            auto_save_interval=BRAIN_AUTO_SAVE_INTERVAL,
        ):
        self.memory = {}
        self.save_path = save_path
        self.max_ram_bytes = max_ram_mb * 1024 * 1024
        self.max_ram_percent = max_ram_percent
        self.auto_save_interval = auto_save_interval
        self.last_save_time = time.time()

        if os.path.exists(self.save_path):
            self.load()

    @trace_method("Brain")
    def learn(self, stimulus, response, outcome=None):
        self.memory[stimulus] = {"response": response}
        self._maybe_save()

    @trace_method("Brain")
    def predict_response(self, stimulus):
        if stimulus in self.memory:
            response = self.memory[stimulus]["response"]
            if response == stimulus:
                return random.choice(FALLBACK_EMOTIONS)
            return response
        return random.choice(FALLBACK_EMOTIONS)

    def _buffer_size_bytes(self):
        return sys.getsizeof(self.memory)

    def _memory_usage_percent(self):
        return psutil.virtual_memory().percent

    def _check_system_memory(self):
        system_memory_usage = psutil.virtual_memory().percent
        if system_memory_usage >= 90:
            self.save()

    def _maybe_save(self):
        now = time.time()
        interval_in_ticks = self.auto_save_interval * TICKS_PER_SECOND
        max_allowed_memory = (self.max_ram_percent / 100) * self.max_ram_bytes

        self._check_system_memory()

        if (
            self._buffer_size_bytes() > self.max_ram_bytes
            or self._memory_usage_percent() > self.max_ram_percent
            or self._buffer_size_bytes() > max_allowed_memory
            or now - self.last_save_time > interval_in_ticks
        ):
            self.save()
            self.last_save_time = now

    def save(self):
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "wb") as f:
            pickle.dump(self.memory, f)

    def force_save(self):
        self.save()
        self.last_save_time = time.time()

    def load(self):
        with open(self.save_path, "rb") as f:
            self.memory = pickle.load(f)
