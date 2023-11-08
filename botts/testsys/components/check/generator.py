from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random
from typing import Any, Callable, Sequence


@dataclass
class Arguments:
    args: tuple[Any]
    kwargs: dict[str, Any]


class Generator(ABC):
    @abstractmethod
    def __call__(self, random: Random, *args, **kwargs) -> Any:
        pass

    def repeat(self, number: int, as_type: type = tuple) -> 'Generator':
        class RepeatingGenerator(Generator):
            def __call__(_, random: Random, *args, **kwargs) -> Any:
                return as_type([self(random, *args, **kwargs) for _ in range(number)])

        return RepeatingGenerator()

    def retry_until(self, fn: Callable) -> 'Generator':
        class RetryGenerator(Generator):
            def __call__(_, random: Random, *args, **kwargs) -> Any:
                value = self(random, *args, **kwargs)
                while not fn(value):
                    value = self(random, *args, **kwargs)
                return value

        return RetryGenerator()

    def map(self, fn: Callable[[Any], Any]) -> 'Generator':
        class MapGenerator(Generator):
            def __call__(_, random: Random, *args, **kwargs) -> Any:
                value = self(random, *args, **kwargs)
                mapped_value = fn(value)
                if isinstance(mapped_value, Generator):
                    mapped_value = mapped_value(random, *args, **kwargs)
                return mapped_value

        return MapGenerator()


class _Helpers:
    @staticmethod
    def distinct(value: Any):
        if not isinstance(value, Sequence):
            return True
        sub_values = set(value)
        return len(sub_values) == len(value)

    @staticmethod
    def repeat_test(gen_object: Generator | Any, number: int):
        return [gen_object for _ in range(number)]


H = _Helpers


def delay(generator: type) -> Callable:
    instance = generator()

    def initialize(*args, **kwargs):
        class DelayedGenerator(Generator):
            # noinspection PyMethodOverriding
            def __call__(self, random: Random) -> Any:
                return instance(random, *args, **kwargs)

        return DelayedGenerator()

    return initialize


def generate(gen_object: Generator | Any, random: Random) -> Any:
    if isinstance(gen_object, Generator):
        return gen_object(random)
    return gen_object


class RandomInteger(Generator):
    # noinspection PyMethodOverriding
    def __call__(self, random: Random, low: int, high: int) -> int:
        return random.randint(low, high)


class RandomFloat(Generator):
    # noinspection PyMethodOverriding
    def __call__(self, random: Random, low: float, high: float) -> float:
        return random.uniform(low, high)


R_INT = delay(RandomInteger)
R_FLOAT = delay(RandomFloat)


class ArgList(Generator):
    def __init__(self, *sub_gens: Generator | Any):
        self.sub_gens = sub_gens

    def __call__(self, random: Random) -> Any:
        return Arguments(
            tuple([generate(sub_gen, random) for sub_gen in self.sub_gens]),
            {}
        )
