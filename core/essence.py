from core.logger import trace_method

class Essence:
    def __init__(self):
        self.respond_mode = True
        self.self_expression_mode = True

    @trace_method("Essence")
    def should_express(self, being):
        return being.state.active == 1
