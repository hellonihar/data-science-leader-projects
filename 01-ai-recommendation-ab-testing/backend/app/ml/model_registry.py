import logging
import os
import pickle
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class ModelRegistry:
    def __init__(self):
        self.registry_path = Path(settings.model_registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self._models = {}

    def save_model(self, name: str, model_obj) -> None:
        path = self.registry_path / f"{name}.pkl"
        with open(path, "wb") as f:
            pickle.dump(model_obj, f)
        logger.info("Saved model '%s' to %s", name, path)

    def load_model(self, name: str):
        if name in self._models:
            return self._models[name]

        path = self.registry_path / f"{name}.pkl"
        if not path.exists():
            logger.warning("Model '%s' not found at %s", name, path)
            return None

        with open(path, "rb") as f:
            model = pickle.load(f)
        self._models[name] = model
        logger.info("Loaded model '%s' from %s", name, path)
        return model

    def list_models(self) -> list[str]:
        return [f.stem for f in self.registry_path.glob("*.pkl")]
