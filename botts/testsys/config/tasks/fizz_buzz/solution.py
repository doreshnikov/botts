def get_fizz_buzz(n: int) -> list[int | str]:
    """
    If value divided by 3 - "Fizz",
       value divided by 5 - "Buzz",
       value divided by 15 - "FizzBuzz",
    else - value.
    :param n: size of sequence
    :return: list of values.
    """
    nums: list[int | str] = list(range(1, n + 1))
    for i in range(len(nums)):
        if nums[i] % 15 == 0:
            nums[i] = "FizzBuzz"
        elif nums[i] % 5 == 0:
            nums[i] = "Buzz"
        elif nums[i] % 3 == 0:
            nums[i] = "Fizz"
    return nums
