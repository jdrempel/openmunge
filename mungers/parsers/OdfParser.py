import re


class OdfParser:
    SECTION_BEGIN = '['
    COMMENT_BEGIN = '//'
    SECTION_NAME_RE = re.compile(r'^\[(?P<name>[A-Za-z0-9_]+)]')
    KEY_VALUE_RE = re.compile(r'^(?P<key>[A-Za-z0-9_]+)\s*=\s*(?P<value>[^/]+)')

    def parse_file(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()
        sections = dict()
        current_section = None
        for line in lines:
            stripped_line = line.strip(' \t\r\n')
            if not stripped_line:
                continue
            if stripped_line.startswith(self.COMMENT_BEGIN):
                continue
            if stripped_line.startswith(self.SECTION_BEGIN):
                section_name = self.SECTION_NAME_RE.match(stripped_line).group('name')
                if not section_name:
                    continue
                sections[section_name] = []
                current_section = section_name
                continue
            if current_section is None:
                continue
            key_value = self.KEY_VALUE_RE.match(stripped_line)
            if not key_value:
                continue
            key = key_value.group('key').strip(' \t\r\n')
            value = key_value.group('value').strip('" \t\r\n')
            if not value:
                continue
            if key in ('ClassLabel', 'ClassParent'):
                sections['__class_name'] = (value, key == 'ClassParent')
                continue
            pair = (key, value)
            sections[current_section].append(pair)

        return sections
