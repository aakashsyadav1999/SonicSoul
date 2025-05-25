# /D:/vscode/SonicSoul/SonicSoul/src/middleware/feature_branching.py

class FeatureBranching:
    """
    Middleware to enable or disable features dynamically.
    """

    def __init__(self, features=None):
        """
        Initialize with a dictionary of feature flags.
        :param features: dict, e.g. {'feature_x': True, 'feature_y': False}
        """
        self.features = features or {}

    def is_enabled(self, feature_name):
        """
        Check if a feature is enabled.
        :param feature_name: str
        :return: bool
        """
        return self.features.get(feature_name, False)

    def enable(self, feature_name):
        """
        Enable a feature.
        """
        self.features[feature_name] = True

    def disable(self, feature_name):
        """
        Disable a feature.
        """
        self.features[feature_name] = False

    def toggle(self, feature_name):
        """
        Toggle a feature's enabled state.
        """
        self.features[feature_name] = not self.features.get(feature_name, False)