from decimal import Decimal


def is_integer(num: Decimal) -> bool:
    return num == num.to_integral_value()


def is_perfect_square(num: Decimal) -> bool:
    if num < 0:
        return False
    return is_integer(num.sqrt())


def is_prime(num: Decimal) -> bool:
    if not is_integer(num):
        return False
    n = int(num)
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(num.sqrt()) + 1, 2):
        if n % i == 0:
            return False
    return True