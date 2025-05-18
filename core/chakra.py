import random
from core.logger import trace_method
from core.config import (
    CHAKRA_ENERGY_GAIN,
    CHAKRA_SATURATION_GAIN,
    DEFAULT_EMOTION,
    FALLBACK_EMOTIONS
)

class Chakra:
    def __init__(self, name, receptivity=1.0):
        self.name = name
        self.energy = 1.0
        self.receptivity = receptivity
        self.saturation = 0.0

    @trace_method("Chakra")
    def receive(self, vibration):
        if vibration.chakra == self.name:
            delta = vibration.intensity * self.receptivity
            self.energy += delta * CHAKRA_ENERGY_GAIN
            self.saturation += delta * CHAKRA_SATURATION_GAIN
            return delta
        return 0

    @trace_method("Chakra")
    def predict_response(self, stimulus):
        if hasattr(self, "memory") and stimulus in self.memory:
            return self.memory[stimulus].get("emotion", DEFAULT_EMOTION)
        else:
            return random.choice(FALLBACK_EMOTIONS)
