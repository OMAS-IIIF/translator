from deepl import DeepLClient

from paraglidetranslator.components.singleton import singleton


@singleton
class DeepLConnection:
    client: DeepLClient
    deepl_key: str

    def __init__(self, deepl_key: str | None = None):
        if deepl_key is not None:
            self.deepl_key = deepl_key
            self.client = DeepLClient(deepl_key)