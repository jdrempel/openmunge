def strcmp_i(a: str, b: str) -> bool:
    return a.casefold() == b.casefold()


def str_in_i(inner: str, outer: str) -> bool:
    return inner.casefold() in outer.casefold()
