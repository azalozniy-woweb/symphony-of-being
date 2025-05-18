from core.logger import trace_method

class Vibration:
    def __init__(self, frequencies, intensity, emotion, chakra, word, source):
        self.frequencies = frequencies
        self.intensity = intensity
        self.emotion = emotion
        self.chakra = chakra
        self.word = word
        self.source = source

    @trace_method("Vibration")
    def merge(self, other_vibration):
        combined_frequencies = list(set(self.frequencies + other_vibration.frequencies))
        combined_intensity = min(self.intensity + other_vibration.intensity, 1.0)
        combined_emotion = self.emotion if self.intensity >= other_vibration.intensity else other_vibration.emotion
        combined_chakra = self.chakra if self.intensity >= other_vibration.intensity else other_vibration.chakra

        return Vibration(
            frequencies=combined_frequencies,
            intensity=combined_intensity,
            emotion=combined_emotion,
            chakra=combined_chakra,
            word="Merged",
            source="merged"
        )
