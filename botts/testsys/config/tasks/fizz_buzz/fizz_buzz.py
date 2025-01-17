LEGEND = """
Вернуть список чисел от 1 до n. При этом вместо чисел, кратных трем, там должно быть слово "Fizz", 
а вместо чисел, кратных пяти — слово "Buzz". Если число кратно и 3, и 5, то вместо них должно быть  слово "FizzBuzz".

* Постарайтесь написать самый простой и читабельный вариант решения
* Постарайтесь написать задачу за 5 минут и с первого раза

### Пример

```python
In [1]: from fizz_buzz.fizz_buzz import get_fizz_buzz

In [2]: get_fizz_buzz(3)
Out[2]: [1, 2, "Fizz"]
```
"""


def get_fizz_buzz(n: int) -> list[int | str]:
    """
    If value divided by 3 - "Fizz",
       value divided by 5 - "Buzz",
       value divided by 15 - "FizzBuzz",
    else - value.
    :param n: size of sequence
    :return: list of values.
    """
    pass
