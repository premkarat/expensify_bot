class DB:
    def __init__(self):
        self._keystore = {}

    def save(self, item, value):
        self._keystore[item] = value

    def get(self, item):
        return self._keystore.get(item)

    def remove(self, item):
        self._keystore.pop(item, None)

    def items(self):
        return list(self._keystore.keys())