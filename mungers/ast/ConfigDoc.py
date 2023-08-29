from core.util.hashing import magic
from mungers.chunks.Chunk import Chunk


class ConfigDoc(Chunk):
    def __init__(self):
        super().__init__('cnfg')
        self._config_name = None
        self.instances = []

    def __repr__(self):
        return 'ConfigDoc[{}]'.format(len(self.instances))

    @property
    def config_name(self):
        return self._config_name

    @config_name.setter
    def config_name(self, value):
        if not isinstance(value, str):
            raise TypeError('ConfigDoc name must be type str.')
        self._config_name = magic(value)

    @staticmethod
    def build(tok):
        config = ConfigDoc()
        config.instances = tok.as_list()
        return config
