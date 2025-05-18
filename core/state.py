from core.logger import trace_method
from core.config import MIN_ENERGY_THRESHOLD, ENERGY_RECHARGE_RATE, MOOD_DEFAULT

class State:
    def __init__(self):
        self.energy = 1.0
        self.active = 1
        self.min_energy_threshold = MIN_ENERGY_THRESHOLD
        self.energy_recharge_rate = ENERGY_RECHARGE_RATE
        self.mood = MOOD_DEFAULT

    @trace_method("State")
    def update(self):
        if self.energy < self.min_energy_threshold:
            self.energy = min(self.energy + self.energy_recharge_rate, 1.0)
            if self.active == 0:
                self.active = 1
