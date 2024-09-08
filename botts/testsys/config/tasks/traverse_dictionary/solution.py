import typing as tp


def traverse_dictionary(
        dct: tp.Mapping[str, tp.Any],
        prefix: str = "") -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param prefix: prefix for key used for passing total path through recursion
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    result = []
    for key, value in dct.items():
        if isinstance(value, dict):
            result += traverse_dictionary(value, prefix + key + ".")
        else:
            result.append((prefix + key, value))
    return result
