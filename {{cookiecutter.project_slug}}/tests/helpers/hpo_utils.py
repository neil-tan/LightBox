"""HPO testing utilities for {{cookiecutter.project_name}}."""


class MockTrial:
    """Mock Optuna trial for deterministic testing.

    Returns predictable values for each suggestion type:
    - categorical: first choice
    - float: midpoint of range
    - int: midpoint (respecting step)

    Usage:
        trial = MockTrial()
        config = search_space(trial, base_config)
        assert trial.params["lr"] == expected_value
    """

    def __init__(self):
        self.params = {}
        self._suggestion_counts = {}

    def suggest_categorical(self, name, choices):
        """Return first choice for deterministic testing."""
        self._suggestion_counts[name] = self._suggestion_counts.get(name, 0) + 1
        value = choices[0]
        self.params[name] = value
        return value

    def suggest_float(self, name, low, high, **kwargs):
        """Return midpoint of range for deterministic testing."""
        self._suggestion_counts[name] = self._suggestion_counts.get(name, 0) + 1
        if kwargs.get("log", False):
            # Log scale: geometric mean
            import math
            value = math.sqrt(low * high)
        else:
            value = (low + high) / 2
        self.params[name] = value
        return value

    def suggest_int(self, name, low, high, **kwargs):
        """Return midpoint of range for deterministic testing."""
        self._suggestion_counts[name] = self._suggestion_counts.get(name, 0) + 1
        step = kwargs.get("step", 1)
        value = low + ((high - low) // (2 * step)) * step
        self.params[name] = value
        return value
