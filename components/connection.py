from deepl import DeepLClient

from components.singleton import singleton


@singleton
class Connection:
    client: DeepLClient

    def __init__(self, deepl_key: str | None = None):
        if deepl_key is not None:
            self.client = DeepLClient(deepl_key)