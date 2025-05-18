import json
import random
from core.logger import trace_method

class Genome:
    def __init__(self, parent1=None, parent2=None, base_archetype="child"):
        if base_archetype == "child":
            with open("child.json", "r", encoding="utf-8") as f:
                self.base_archetype = json.load(f)
        else:
            self.base_archetype = base_archetype
        
        self.traits = self.combine_traits(parent1, parent2)
        self.dominant_chakra = self.combine_chakra(parent1, parent2)
        self.emotional_focus = self.combine_focus(parent1, parent2)

    @trace_method("Genome")
    def combine_traits(self, parent1, parent2):
        if parent1 and parent2:
            return {key: (parent1.traits.get(key, 0) + parent2.traits.get(key, 0)) / 2 for key in parent1.traits}
        if isinstance(self.base_archetype, dict):
            return self.base_archetype["traits"]
        return {"strength": 5, "intelligence": 4}

    @trace_method("Genome")
    def combine_chakra(self, parent1, parent2):
        if isinstance(self.base_archetype, dict):
            return parent1.dominant_chakra if parent1 else self.base_archetype["dominant_chakra"]
        return parent1.dominant_chakra if parent1 else "svadhisthana"

    @trace_method("Genome")
    def combine_focus(self, parent1, parent2):
        if parent1 and parent2:
            return list(set(parent1.emotional_focus + parent2.emotional_focus))
        if isinstance(self.base_archetype, dict):
            return self.base_archetype["emotional_focus"]
        return ["удивление", "радость"]
