

class Controller:
    """
    Very simple adaptive trust controller.

    weight ∈ [0, 1000]  → displayed as 0.00–1.00
    theta  ∈ [50, 500]  → displayed as 0.50–5.00
    """

    def __init__(self):
        self.state = {}

    def _ensure(self, model_id):
        if model_id not in self.state:
            self.state[model_id] = {"weight": 500, "theta": 250}

    def update(self, model_id, valid: bool):
        self._ensure(model_id)
        st = self.state[model_id]

        if valid:
            st["weight"] = min(1000, st["weight"] + 30)
            st["theta"] = max(50, st["theta"] - 8)
        else:
            st["weight"] = max(0, st["weight"] - 100)
            st["theta"] = min(500, st["theta"] + 30)

    def summary(self):
        return self.state
