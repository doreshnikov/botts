import typing as tp


LEGEND = """
Написать функцию, которая выворачивает словарь. То есть значения становятся ключами, а ключи - списком значений.

* Не мутируйте входной словарь
* Если вы используете `defaultdict`, то стоит его преобразовать к `dict` при return
* Порядок элементов в списках не важен

### Пример

```python
>>> revert({"a": "1", "b": "2", "c": "1"})
{"1": ["a", "c"], "2": ["b"]})
```
"""


def revert(dct: tp.Mapping[str, str]) -> dict[str, list[str]]:
    """
    :param dct: dictionary to revert in format {key: value}
    :return: reverted dictionary {value: [key1, key2, key3]}
    """
    pass
