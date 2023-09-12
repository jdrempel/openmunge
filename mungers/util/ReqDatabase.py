import pathlib
from collections import OrderedDict
from contextlib import contextmanager


class ReqSection(list):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ReqDatabase(metaclass=SingletonMeta):
    """A singleton (per process) that tracks requirement database entries and writes them to a .req file."""
    def __init__(self):
        self.sections = OrderedDict()

    def get_section(self, name: str) -> ReqSection:
        if name not in self.sections:
            self.sections[name] = ReqSection(name)
        return self.sections[name]

    @contextmanager
    def open_section(self, name: str):
        if name not in self.sections:
            self.sections[name] = ReqSection(name)
        yield self.sections[name]

    def write(self, path: pathlib.Path):
        def quote(s: str) -> str:
            return '"{}"'.format(s.strip('"'))
        with path.open('w', newline='\r\n') as f:
            lines = ['', 'ucft', '{']
            for section in self.sections.values():
                section_unique = list(dict.fromkeys(section))
                section_lines = ['REQN', '{', '\t' + quote(section.name)]
                section_lines.extend(['\t' + quote(item.lower()) for item in section_unique])
                section_lines.append('}')
                lines.extend(['\t' + line for line in section_lines if line.strip()])
            lines.append('}')
            f.write('\n'.join(lines))

    def clear(self):
        self.sections.clear()
