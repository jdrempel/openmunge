from dataclasses import dataclass


@dataclass
class ParserOptions:
    document_cls: type = None
    all_numbers_are_floats: bool = True
    all_values_are_strings: bool = False
