import typing as tp
from collections import defaultdict


def revert(dct: tp.Mapping[str, str]) -> dict[str, list[str]]:
    """
    :param dct: dictionary to revert in format {key: value}
    :return: reverted dictionary {value: [key1, key2, key3]}
    """
    reverted_dict = defaultdict(list)

    for key, value in dct.items():
        reverted_dict[value].append(key)

    return dict(reverted_dict)
