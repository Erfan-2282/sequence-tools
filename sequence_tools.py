from typing import cast, List


class MyCount:
    def __init__(self, start=1, step=1):
        self.current = start
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        val = self.current
        self.current += self.step
        return val

    def decrement(self):
        self.current -= 1


def _get_user_choice(text: str):
    print(f"""[INPUT] Your sequence is {text}. Please choose what you want to do with this sequence:

1. Find the nth term of the sequence


2. Find the formula of the sequence


3. Find the sum of the first n terms of the sequence

Enter your choice (1-3):""")
    user_choice = 0  # To prevent Pylance "report unbound variable" error
    while True:
        try:
            user_choice = int(input())
        except ValueError:
            not_valid_number = True
        else:
            not_valid_number = False
        if not_valid_number or not 1 <= user_choice <= 3:
            print(
                "[ERROR] Invalid input. Please enter the number of your chosen option.")
        else:
            break
    return user_choice


def _get_n():
    print("[INPUT] Please enter the position (n) of the term in the sequence:")
    while True:
        try:
            n = int(input())
        except ValueError:
            print("[ERROR] Invalid input. Please enter an integer number.")
        else:
            if n <= 0:
                print("[ERROR] Invalid input. Input cannot be zero or negative.")
            else:
                return n


def _quadratic_coefficients(sequence: List[int]):
    a1, a2, a3 = sequence[:3]
    a_coef = (a3 - 2 * a2 + a1) / 2
    b_coef = a2 - a1 - 3 * a_coef
    c_coef = a1 - a_coef - b_coef
    return a_coef, b_coef, c_coef


def _get_prime_numbers(n: int, only_nth: bool = True):
    prime_numbers = [2]
    count = MyCount(start=3, step=2)
    for num in count:
        if len(prime_numbers) == n:
            break
        if all(num % i != 0 for i in range(3, int(num ** 0.5) + 1, 2)):
            prime_numbers.append(num)
    if not only_nth:
        return prime_numbers
    return prime_numbers[-1]


def get_sequence():
    count = MyCount()
    print("[INPUT] Please enter the numbers of your sequence in order.\nWhen you are done, type: 'finish'.")
    user_sequence = []
    for i in count:
        user_input = input(f"{i}: ")
        if user_input.lower() == "finish" and len(user_sequence) >= 3:
            break
        try:
            user_input = int(user_input)
        except ValueError:
            print(
                "[ERROR] Invalid input. Your sequence numbers must be integers and contain at least three elements.")
            count.decrement()
        else:
            user_sequence.append(user_input)
    return user_sequence


def detect_sequence_type(sequence: List[int]):
    if all(sequence[i] - sequence[i - 1] == sequence[1] - sequence[0] for i in range(2, len(sequence))):
        return "arithmetic"
    elif all(sequence[0] != 0 and sequence[i] / sequence[i - 1] == sequence[1] / sequence[0] for i in range(2, len(sequence))):
        return "geometric"
    elif all(sequence[i - 1] == (i * (i + 1)) // 2 for i in range(1, len(sequence))):
        return "triangular"
    elif sequence == _get_prime_numbers(n=len(sequence), only_nth=False):
        return "prime"
    elif all(sequence[i] == sequence[i - 1] + sequence[i - 2] for i in range(2, len(sequence))):
        return "fibonacci"
    elif all(sequence[i] - 2 * sequence[i - 1] + sequence[i - 2] == sequence[2] - 2 * sequence[1] + sequence[0] for i in range(3, len(sequence))) if len(sequence) > 3 else (lambda a_coef, b_coef, c_coef:
                                                                                                                                                                             sequence[0] == a_coef + b_coef + c_coef and
                                                                                                                                                                             sequence[1] == 4 * a_coef + 2 * b_coef + c_coef and
                                                                                                                                                                             sequence[
                                                                                                                                                                                 2] == 9 * a_coef + 3 * b_coef + c_coef
                                                                                                                                                                             )(*_quadratic_coefficients(sequence)): # type: ignore
        return "quadratic"


def arithmetic_sequence(sequence: List[int]):
    print(sequence)
    user_choice = _get_user_choice("an arithmetic sequence")
    a = sequence[0]
    d = sequence[1] - sequence[0]
    if user_choice == 1:
        n = _get_n()
        print(f"[RESULT] Answer: {a + (n - 1) * d}")
    elif user_choice == 2:
        print(
            f"[RESULT] Formula of your sequence:\nTn = n × {d} + {sequence[0] - d}")
    else:
        n = _get_n()
        print(f"[RESULT] Answer: {n * (2 * a + (n - 1) * d) / 2: ,}")


def geometric_sequence(sequence: List[int]):
    print(sequence)
    user_choice = _get_user_choice("a geometric sequence")
    r = sequence[1] / sequence[0]
    a = sequence[0]
    if user_choice == 1:
        n = _get_n()
        print(f"[RESULT] Answer: {a * r ** (n- 1): ,}")
    elif user_choice == 2:
        print(f"[RESULT] Formula of your sequence:\nTn = {a} × {r}^(n - 1)")
    else:
        n = _get_n()
        try:
            print(f"[RESULT] Answer: {a * (1 - r ** n) / (1 - r): ,}")
        except ZeroDivisionError:
            print(f"[RESULT] Answer: {a * n: ,}")


def quadratic_sequence(sequence: List[int]):
    print(sequence)
    user_choice = _get_user_choice("a quadratic sequence")
    a_coef, b_coef, c_coef = _quadratic_coefficients(sequence)
    if user_choice == 1:
        n = _get_n()
        print(f"[RESULT] Answer: {a_coef * n**2 + b_coef * n + c_coef: ,}")
    elif user_choice == 2:
        print(
            f"[RESULT] Formula of your sequence:\nTn = "
            f"{'n^2' if a_coef == 1 else '-n^2' if a_coef == -1 else f'{a_coef} × n^2'}"
            f"{'' if b_coef == 0 else (' + n' if b_coef == 1 else ' - n' if b_coef == -1 else f' + {b_coef} × n' if b_coef > 0 else f' - {abs(b_coef)} × n')}"
            f"{'' if c_coef == 0 else (f' + {c_coef}' if c_coef > 0 else f' - {abs(c_coef)}')}"
        )
    else:
        n = _get_n()
        n1 = n * (n + 1)
        print(
            f"[RESULT] Answer: {((a_coef * n1 * (2 * n + 1)) / 6) + ((b_coef * n1) / 2) + (c_coef * n): ,}")


def triangular_sequence(sequence: List[int]):
    print(sequence)
    user_choice = _get_user_choice("a triangular sequence")
    if user_choice == 1:
        n = _get_n()
        print(f"[RESULT] Answer: {(n * (n + 1)) / 2: ,}")
    elif user_choice == 2:
        print(f"[RESULT] Formula of your sequence:\nTn = (n × (n + 1)) ÷ 2")
    else:
        n = _get_n()
        print(f"[RESULT] Answer: {(n * (n + 1) * (n + 2)) / 6: ,}")


def fibonacci_sequence(sequence: List[int]):
    print(sequence)
    user_choice = _get_user_choice("a fibonacci sequence")
    if user_choice == 1:
        n = _get_n()
        seq_list = sequence[:3]
        while len(seq_list) < n:
            seq_list.append(seq_list[-1] + seq_list[-2])
        print(f"[RESULT] Answer: {seq_list[-1]: ,}")
    elif user_choice == 2:
        print(f"[RESULT] Formula of your sequence:\nTn = Tn₋₁ + Tn₋₂")
    else:
        n = _get_n()
        seq_list = sequence[:3]
        while len(seq_list) < n:
            seq_list.append(seq_list[-1] + seq_list[-2])
        print(f"[RESULT] Answer: {sum(seq_list[:n]): ,}")


def prime_sequence(sequence: List[int]):
    print(sequence)
    user_choice = _get_user_choice("a prime sequence")
    if user_choice == 1:
        n = _get_n()
        print(f"[RESULT] Answer: {_get_prime_numbers(n): ,}")
    elif user_choice == 2:
        print(f"[RESULT] There is no simple formula for generating the nth prime number.\nPrime numbers are calculated using iterative checks for primality.")
    else:
        n = _get_n()
        print(
            f"[RESULT] Answer: {sum(cast(List[int], _get_prime_numbers(n, only_nth=False))): ,}")


