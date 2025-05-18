from collections import deque
from core.logger import trace_method, log_input, flush_tick
from core.memory import Memory
from core.state import State
from core.brain import Brain
from core.chakra import Chakra
from core.vibration import Vibration
from core.config import (
    DEFAULT_SPEAK_MODE,
    SILENCE_THRESHOLD,
    EXPRESSION_THRESHOLD,
    REFLECTION_THRESHOLD,
    ENERGY_DECAY_RATE,
    TRUST_DROP_THRESHOLD,
    DECAY_MULTIPLIER,
    MERGE_THRESHOLD_HIGH,
    VIBRATION_DECAY_RATE,
    FALLBACK_EMOTIONS,
    EMOTION_MAP,
    CHAKRA_MAP,
    DEFAULT_EMOTION_LABEL,
    DEFAULT_CHAKRA_LABEL
)

class VibrationalBeing:
    def __init__(self, base_archetype="poet"):
        self.tick = 0
        self.base_archetype = base_archetype

        self.speak_mode = DEFAULT_SPEAK_MODE
        self.silence_threshold = SILENCE_THRESHOLD
        self.expression_threshold = EXPRESSION_THRESHOLD
        self.reflection_threshold = REFLECTION_THRESHOLD

        self.energy_decay_rate = ENERGY_DECAY_RATE
        self.decay_multiplier = DECAY_MULTIPLIER
        self.trust_drop_threshold = TRUST_DROP_THRESHOLD

        self.vibration_decay = VIBRATION_DECAY_RATE
        self.merge_threshold_high = MERGE_THRESHOLD_HIGH

        self.is_resonating = False
        self.input_queue = deque()
        self.sentence_queue = deque()
        self.sentence_buffer = []
        self.last_signal = None
        self.vibrations = []

        self.memory = Memory()
        self.state = State()
        self.brain = Brain()
        self.chakras = {}

    @trace_method("VibrationalBeing")
    def enqueue_input(self, input_signal: str):
        if input_signal.strip():
            words = input_signal.strip().lower().split()
            if len(words) > 1:
                self.sentence_queue.append(words)
            else:
                self.input_queue.append(input_signal.strip().lower())

    @trace_method("VibrationalBeing")
    def update(self):
        if not self.is_resonating and not self.input_queue and not self.sentence_queue:
            return

        if not self.is_resonating and (self.input_queue or self.sentence_queue):
            self.is_resonating = True
            self.state.active = 1

        self.tick += 1
        self.state.update()

        if self.input_queue:
            current_input = self.input_queue.popleft()
            self.last_signal = current_input
            log_input(self.tick, current_input)
            response = self.brain.predict_response(current_input)
            self.react(response, is_sentence=False)

        if self.sentence_queue:
            sentence_words = self.sentence_queue.popleft()
            self.sentence_buffer.extend(sentence_words)

            for word in sentence_words:
                self.input_queue.append(word)

            if len(self.sentence_buffer) == len(sentence_words):
                sentence_response = self.brain.predict_response(" ".join(self.sentence_buffer))
                self.react(sentence_response, is_sentence=True)
                self.sentence_buffer.clear()

        flush_tick(self.tick)

    @trace_method("VibrationalBeing")
    def _resonance_tick(self):
        if not self.last_signal:
            return
        response = self.brain.predict_response(self.last_signal)
        self.react(response, is_sentence=False)

    @trace_method("VibrationalBeing")
    def react(self, response, is_sentence=False):
        if response == "тишина" or not response:
            return

        vibration = self.forge_vibration(response)
        self.vibrations.append(vibration)

        ch_name = vibration.chakra
        if ch_name in self.chakras:
            if not isinstance(self.chakras[ch_name], Chakra):
                self.chakras[ch_name] = Chakra(ch_name)
            self.chakras[ch_name].receive(vibration)

        self.memory.store(vibration)
        self.brain.learn(self.last_signal, response)
        self.last_signal = response

        if is_sentence:
            print(f"Ответ на предложение: {response}")
            log_input(self.tick, f"Ответ на предложение: {response}")

    @trace_method("VibrationalBeing")
    def forge_vibration(self, word, source="resonance"):
        emo = EMOTION_MAP.get(word, DEFAULT_EMOTION_LABEL)
        ch = CHAKRA_MAP.get(word, DEFAULT_CHAKRA_LABEL)
        intensity = 1.0

        return Vibration(
            frequencies=[hash(word) % 100],
            intensity=intensity,
            emotion=emo,
            chakra=ch,
            word=word,
            source=source
        )
