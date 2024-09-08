import typing as tp


LEGEND = """
Написать функцию, которая из словаря генерируют список пар: (ключи, соединенные через точку; значение).

* Не мутируйте входные словари. Старайтесь как можно меньше мутировать используемые структуры
* Подумайте, какая сложность по времени и памяти получилась у трех реализаций? В чем их значимые отличия?

### Пример

```python
from .traverse_dictionary import traverse_dictionary
    "a": 1,
    "b": {
        "c": 2,
        "d": 4
    }
}

>>> traverse_dictionary(d)
[("a", 1), ("b.c", 2), ("b.d", 4)]
```
"""


def traverse_dictionary(
        dct: tp.Mapping[str, tp.Any],
        prefix: str = "") -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param prefix: prefix for key used for passing total path through recursion
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    pass
