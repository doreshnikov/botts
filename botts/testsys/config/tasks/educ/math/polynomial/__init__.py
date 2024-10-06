polynomial = list[int | float]


def polynomial_calculate(p: polynomial, x: int | float) -> int | float:
    value = 0
    power_of_x = 1
    for i, pi in enumerate(p):
        value += pi * power_of_x
        power_of_x *= x
    return value
