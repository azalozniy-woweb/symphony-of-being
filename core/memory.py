from collections import deque
from core.logger import trace_method
from core.config import SHORT_TERM_MEMORY_SIZE, LONG_TERM_THRESHOLD

class Memory:
    def __init__(self):
        self.short_term = deque(maxlen=SHORT_TERM_MEMORY_SIZE)
        self.long_term = []

    @trace_method("Memory")
    def store(self, vibration):
        self.short_term.append(vibration)
        if vibration.intensity > LONG_TERM_THRESHOLD:
            self.long_term.append(vibration)

    @trace_method("Memory")
    def get_most_common_vibrations(self):
        return [vibration.emotion for vibration in self.short_term]
