import operator
from decimal import Decimal
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import (
    Any,
    TypedDict,
    Protocol,
    Required,
    NotRequired,
    Mapping
)
from _math_utils import (
    is_integer,
    is_perfect_square,
    is_prime
)

type _Number = int | float | Decimal
type _Seq = list[_Number]
type _InternalSeq = list[Decimal]
type _Patterns = tuple[type[SequencePattern], ...]


class _Operator(Protocol):
    def __call__(self, left, right, /) -> _Number:
        ...


class _PatternInformation(TypedDict):
    type: Required[type[SequencePattern]]
    extra_info: NotRequired[dict[str, Any]]


class SequencePattern(ABC):
    def __init__(self, sequence: _InternalSeq) -> None:
        self.sequence = sequence

    @staticmethod
    @abstractmethod
    def detector(sequence: _InternalSeq) -> bool:
        ...

    @abstractmethod
    def nth_generator(self, n: int) -> Decimal:
        ...

    @abstractmethod
    def formula_generator(self) -> Formula | None:
        ...

    @abstractmethod
    def information(self) -> _PatternInformation:
        ...


@dataclass
class Expression:
    left: Decimal | str | Expression
    operator: _Operator
    right: Decimal | str | Expression

    def evaluate(self, parameters: Mapping[str, _Number]) -> _Number:
        left = (
            self.left.evaluate(parameters)
            if isinstance(self.left, Expression)
            else parameters[self.left] if isinstance(self.left, str) else self.left
        )

        right = (
            self.right.evaluate(parameters)
            if isinstance(self.right, Expression)
            else parameters[self.right] if isinstance(self.right, str) else self.right
        )

        return self.operator(left, right)


class Formula:
    def __init__(
        self,
        pattern_type: type[SequencePattern],
        parameters: Mapping[str, _Number],
        definition: str,
        expression: Expression | None = None,
        start_index: int = 1
    ) -> None:
        self.pattern_type = pattern_type
        self.parameters = parameters
        self.definition = definition
        self.start_index = start_index
        self.expression = expression
        self.text_formula = definition
        for key, value in parameters.items():
            setattr(self, key, value)
            self.text_formula = self.text_formula.replace(key, str(value))

    def __str__(self) -> str:
        return "a(n) = " + self.text_formula

    def matches_pattern(self, seq_pattern: type[SequencePattern]) -> bool:
        return self.pattern_type is seq_pattern

    def calculate(self) -> _Seq:
        if self.expression is not None:
            return [self.expression.evaluate({"n": n, **self.parameters}) for n in range(self.start_index, self.start_index + 4)]
        raise ValueError("No expression provided for calculation.")


class ArithmeticSequence(SequencePattern):
    def __init__(self, sequence: _InternalSeq) -> None:
        super().__init__(sequence)
        self.common_difference = sequence[1] - sequence[0]

    @staticmethod
    def detector(sequence: _InternalSeq) -> bool:
        difference = sequence[1] - sequence[0]
        for i in range(2, len(sequence)):
            if sequence[i] - sequence[i - 1] != difference:
                return False
        return True

    def nth_generator(self, n: int) -> Decimal:
        return self.common_difference * (n - 1) + self.sequence[0]

    def formula_generator(self) -> Formula:
        return Formula(
            pattern_type=ArithmeticSequence,
            parameters={"d": self.common_difference, "a1": self.sequence[0]},
            definition="a1 + (n - 1) * d",
            expression=Expression(
                left="a1",
                operator=operator.add,
                right=Expression(
                    left=Expression(
                        left="n",
                        operator=operator.sub,
                        right=Decimal(1)
                    ),
                    operator=operator.mul,
                    right="d"
                )
            )
        )

    def information(self) -> _PatternInformation:
        return {"type": ArithmeticSequence, "extra_info": {"common_difference": self.common_difference}}


class GeometricSequence(SequencePattern):
    def __init__(self, sequence: list[Decimal]) -> None:
        super().__init__(sequence)
        self.common_ratio = (
            sequence[1] / sequence[0] if 0 not in sequence else 0
        )

    @staticmethod
    def detector(sequence: _InternalSeq) -> bool:
        if 0 in sequence[:2]:
            if all(num == 0 for num in sequence[1:]):
                return True
            else:
                return False
        common_ratio = sequence[1] / sequence[0]
        for i in range(2, len(sequence)):
            if sequence[i] / sequence[i - 1] != common_ratio:
                return False
        return True

    def nth_generator(self, n: int) -> Decimal:
        return self.sequence[0] * self.common_ratio ** (n - 1)

    def formula_generator(self) -> Formula:
        return Formula(
            pattern_type=GeometricSequence,
            parameters={"r": self.common_ratio, "a1": self.sequence[0]},
            definition="a1 * r^(n - 1)",
            expression=Expression(
                left="a1",
                operator=operator.mul,
                right=Expression(
                    left="r",
                    operator=operator.pow,
                    right=Expression(
                        left="n",
                        operator=operator.sub,
                        right=Decimal(1)
                    )
                )
            )
        )

    def information(self) -> _PatternInformation:
        return {"type": GeometricSequence, "extra_info": {"common_ratio": self.common_ratio}}


class QuadraticSequence(SequencePattern):
    def __init__(self, sequence: list[Decimal]) -> None:
        super().__init__(sequence)
        self.coefficients = self._calculate_quadratic_coefficients()

    def _calculate_quadratic_coefficients(self) -> dict[str, Decimal]:
        first, second, third = self.sequence[:3]
        a_coefficient = (third - 2 * second + first) / 2
        b_coefficient = second - first - 3 * a_coefficient
        c_coefficient = first - b_coefficient - a_coefficient
        return {"a_coefficient": a_coefficient, "b_coefficient": b_coefficient, "c_coefficient": c_coefficient}

    @staticmethod
    def detector(sequence: _InternalSeq) -> bool:
        if (seq_len := len(sequence)) > 3:
            second_difference = sequence[2] - 2 * sequence[1] + sequence[0]
            for i in range(3, seq_len):
                if sequence[i] - 2 * sequence[i - 1] + sequence[i - 2] != second_difference:
                    return False
        return True

    def nth_generator(self, n: int) -> Decimal:
        a_coef = self.coefficients["a_coefficient"]
        b_coef = self.coefficients["b_coefficient"]
        c_coef = self.coefficients["c_coefficient"]
        return a_coef * n**2 + b_coef * n + c_coef

    def formula_generator(self) -> Formula:
        return Formula(
            pattern_type=QuadraticSequence,
            parameters={
                "a": self.coefficients["a_coefficient"],
                "b": self.coefficients["b_coefficient"],
                "c": self.coefficients["c_coefficient"]
            },
            definition="a*n^2 + b*n + c",
            expression=Expression(
                left=Expression(
                    left="a",
                    operator=operator.mul,
                    right=Expression(
                        left="n",
                        operator=operator.pow,
                        right=Decimal(2)
                    )
                ),
                operator=operator.add,
                right=Expression(
                    left=Expression(
                        left="b",
                        operator=operator.mul,
                        right="n"
                    ),
                    operator=operator.add,
                    right="c"
                )
            )
        )

    def information(self) -> _PatternInformation:
        return {"type": QuadraticSequence, "extra_info": {"coefficients": self.coefficients}}


class TriangularSequence(SequencePattern):
    def detector(self, sequence: _InternalSeq) -> bool:
        index: list[Decimal] = []
        for num in sequence:
            if (num >= 0) and (is_integer(n := ((8 * num + 1).sqrt() - 1) / 2 + 1)):
                index.append(n)
                continue
        if any(index[i] - index[i - 1] != 1 for i in range(1, len(index))) or len(index) != len(sequence):
            return False
        self.start_index = int(index[0])
        return True

    def nth_generator(self, n: int) -> Decimal:
        n -= 1
        return Decimal(n * (n - 1)) / 2

    def formula_generator(self) -> Formula:
        return Formula(
            pattern_type=TriangularSequence,
            parameters={},
            definition="n*(n-1)/2",
            expression=Expression(
                left=Expression(
                    left="n",
                    operator=operator.mul,
                    right=Expression(
                        left="n",
                        operator=operator.sub,
                        right=Decimal(1)
                    )
                ),
                operator=operator.truediv,
                right=Decimal(2)
            )
        )

    def information(self) -> _PatternInformation:
        return {"type": TriangularSequence, "extra_info": {"start_index": self.start_index}}


class OriginalFibonacciSequence(SequencePattern):
    def detector(self, sequence: _InternalSeq) -> bool:
        if all(sequence[i] >= 0 and sequence[i - 2] + sequence[i - 1] == sequence[i] for i in range(2, len(sequence))):
            if (
                all(is_integer(num) for num in sequence)
                and all(
                    is_perfect_square(5 * num**2 + 4)
                    or is_perfect_square(5 * num**2 - 4)
                    for num in sequence
                )
            ):
                if sequence[0] == 0:
                    self.start_index = 0
                elif sequence[:2] == [1, 1]:
                    self.start_index = 1
                else:
                    self.start_index = (round((sequence[0] * Decimal(5).sqrt() + Decimal(
                        "0.5")).ln() / ((Decimal(1) + Decimal(5).sqrt()) / Decimal(2)).ln()))
                return True
        return False

    def nth_generator(self, n: int) -> Decimal:
        first = Decimal(0)
        second = Decimal(1)
        for _ in range(2, n):
            first, second = second, first + second
        return second if n > 1 else first

    def formula_generator(self) -> Formula:
        return Formula(
            pattern_type=OriginalFibonacciSequence,
            parameters={},
            definition="F(n-1) + F(n-2)",
        )

    def information(self) -> _PatternInformation:
        return {"type": OriginalFibonacciSequence, "extra_info": {"start_index": self.start_index}}


class FibonacciTypeSequence(SequencePattern):
    def detector(self, sequence: _InternalSeq) -> bool:
        return all(sequence[i - 2] + sequence[i - 1] == sequence[i] for i in range(2, len(sequence)))

    def nth_generator(self, n: int) -> Decimal:
        first = self.sequence[0]
        second = self.sequence[1]
        for _ in range(2, n):
            first, second = second, first + second
        return second if n > 1 else first

    def formula_generator(self) -> Formula:
        return Formula(
            pattern_type=FibonacciTypeSequence,
            parameters={},
            definition="F(n-1) + F(n-2)",
        )

    def information(self) -> _PatternInformation:
        return {"type": FibonacciTypeSequence}


class PrimeNumbersSequence(SequencePattern):
    def detector(self, sequence: _InternalSeq) -> bool:
        if any(sequence[i] <= sequence[i - 1] for i in range(1, len(sequence))):
            return False
        for num in sequence:
            if not is_prime(num):
                return False
        start_index = 0
        for num in range(1, int(sequence[0])):
            if is_prime(Decimal(num)):
                start_index += 1
        self.start_index = start_index
        return True

    def nth_generator(self, n: int) -> Decimal:
        prime_count = 0
        num = 1

        while prime_count < n:
            num += 1
            if is_prime(Decimal(num)):
                prime_count += 1

        return Decimal(num)

    def formula_generator(self) -> None:
        return None

    def information(self) -> _PatternInformation:
        return {"type": PrimeNumbersSequence, "extra_info": {"start_index": self.start_index}}


class Sequence:
    DEFAULT_PATTERNS: _Patterns = (
        ArithmeticSequence, GeometricSequence, QuadraticSequence, TriangularSequence, FibonacciTypeSequence, OriginalFibonacciSequence, PrimeNumbersSequence)

    def __init__(self, sequence: _Seq, patterns: _Patterns = DEFAULT_PATTERNS) -> None:
        self.patterns = patterns
        self.sequence = sequence

    def _set_sequence_type(self):
        self._sequence_type: list[tuple[type[SequencePattern], SequencePattern]] = [
        ]
        for pattern in self._patterns:
            if (seq := (pattern(self._sequence))).detector(self._sequence):
                self._sequence_type.append((pattern, seq))
        if not self._sequence_type:
            raise ValueError(
                "No supported pattern was found for the sequence.")

    def _validate_patterns(self, patterns: type[SequencePattern] | list[type[SequencePattern]] | None) -> list[type[SequencePattern]]:
        if not isinstance(patterns, list):
            patterns = [patterns] if patterns is not None else None
        valid_patterns = [pattern_type for pattern_type,
                          _ in self._sequence_type]

        if patterns is None:
            patterns = valid_patterns
        elif not patterns:
            raise ValueError("'patterns' cannot be empty.")
        elif any(pattern not in valid_patterns for pattern in patterns):
            raise ValueError(
                "One or more patterns are not supported by this sequence."
            )
        return patterns

    @property
    def patterns(self) -> _Patterns:
        return self._patterns

    @patterns.setter
    def patterns(self, new_patterns: _Patterns) -> None:
        if any(not issubclass(pattern, SequencePattern) for pattern in new_patterns):
            raise ValueError("Your patterns are not valid.")
        if not new_patterns:
            raise ValueError("Patterns cannot be empty.")
        self._patterns: _Patterns = new_patterns
        if hasattr(self, "_sequence_type"):
            self._set_sequence_type()

    @property
    def sequence(self) -> _InternalSeq:
        return self._sequence[:]

    @sequence.setter
    def sequence(self, sequence: _Seq) -> None:
        if not isinstance(sequence, list) or not all(type(x) in (int, float, Decimal) for x in sequence):
            raise ValueError("Sequence must be a list of numbers.")
        if len(sequence) < 3:
            raise ValueError("Sequence must contain at least 3 numbers.")
        self._sequence: _InternalSeq = [Decimal(str(x)) for x in sequence]
        self._set_sequence_type()

    @property
    def sequence_type(self) -> list[type[SequencePattern]]:
        return [seq_type[0] for seq_type in self._sequence_type]

    def is_arithmetic(self) -> bool:
        return any(ArithmeticSequence == pattern[0] for pattern in self._sequence_type)

    def is_geometric(self) -> bool:
        return any(GeometricSequence == pattern[0] for pattern in self._sequence_type)

    def is_quadratic(self) -> bool:
        return any(QuadraticSequence == pattern[0] for pattern in self._sequence_type)

    def is_triangular(self) -> bool:
        return any(TriangularSequence == pattern[0] for pattern in self._sequence_type)

    def is_fibonacci(self) -> bool:
        return any(
            (FibonacciTypeSequence == pattern[0]
             or OriginalFibonacciSequence == pattern[0])
            for pattern in self._sequence_type
        )

    def is_original_fibonacci(self) -> bool:
        return any(OriginalFibonacciSequence == pattern[0] for pattern in self._sequence_type)

    def is_prime_numbers(self) -> bool:
        return any(PrimeNumbersSequence == pattern[0] for pattern in self._sequence_type)

    def matches(self, pattern: type[SequencePattern]) -> bool:
        return pattern in self.sequence_type

    def nth_term(
        self,
        n: int,
        *,
        patterns: type[SequencePattern] |
        list[type[SequencePattern]] | None = None,
        use_start_index: bool = False
    ) -> Decimal | dict[type[SequencePattern], Decimal]:
        if n < 1:
            raise ValueError("'n' cannot be less than 1.")
        patterns = self._validate_patterns(patterns)

        result: dict[type[SequencePattern], Decimal] = {}

        for pattern in patterns:
            seq_pattern = next(
                instance
                for pattern_type, instance in self._sequence_type
                if pattern_type is pattern
            )

            num = n

            if use_start_index:
                extra_info = seq_pattern.information().get("extra_info", {})
                if "start_index" in extra_info:
                    num += extra_info["start_index"]

            result[pattern] = seq_pattern.nth_generator(num)
        if len(result) > 1:
            return result

        return next(iter(result.values()))

    def nth_terms(
        self,
        start: int,
        stop: int,
        patterns: type[SequencePattern] |
        list[type[SequencePattern]] | None = None,
        use_start_index: bool = False
    ) -> _InternalSeq | dict[type[SequencePattern], _InternalSeq]:
        patterns = self._validate_patterns(patterns)
        if start < 1:
            raise ValueError("'start' cannot be less than 1.")
        if stop < start:
            raise ValueError("'stop' cannot be less than 'start'.")
        result: dict[type[SequencePattern], _InternalSeq] = {}
        for pattern in patterns:
            seq_pattern = next(
                instance
                for pattern_type, instance in self._sequence_type
                if pattern_type is pattern
            )
            new_start = start
            new_stop = stop
            if use_start_index:
                extra_info = seq_pattern.information().get("extra_info", {})
                if "start_index" in extra_info:
                    new_start += extra_info["start_index"]
                    new_stop += extra_info["start_index"]
            seq = []
            for n in range(new_start, new_stop + 1):
                seq.append(seq_pattern.nth_generator(n))
            result[pattern] = seq
        if len(result) > 1:
            return result

        return next(iter(result.values()))

    def formula(self, *, patterns: type[SequencePattern] | list[type[SequencePattern]] | None = None) -> Formula | dict[type[SequencePattern], Formula | None] | None:
        patterns = self._validate_patterns(patterns)
        result: dict[type[SequencePattern], Formula | None] = {}
        for pattern in patterns:
            result[pattern] = next(
                instance.formula_generator()
                for pattern_type, instance in self._sequence_type
                if pattern_type is pattern
            )
        if len(result) > 1:
            return result

        return next(iter(result.values()))

    def pattern_info(self, *, patterns: type[SequencePattern] | list[type[SequencePattern]] | None = None) -> _PatternInformation | dict[type[SequencePattern], _PatternInformation]:
        patterns = self._validate_patterns(patterns)
        result: dict[type[SequencePattern], _PatternInformation] = {}
        for pattern in patterns:
            result[pattern] = next(
                instance.information()
                for pattern_type, instance in self._sequence_type
                if pattern_type is pattern
            )
        if len(result) > 1:
            return result

        return next(iter(result.values()))

    @classmethod
    def from_formula(cls, formula: Formula, *, force_pattern: bool = False, try_text_definition: bool = False) -> Sequence:
        if not isinstance(formula, Formula):
            raise ValueError("'formula' must be an instance of Formula.")
        if formula.expression is None:
            if try_text_definition:
                try:
                    sequence = [eval(formula.definition, {"n": n, **formula.parameters})
                                for n in range(formula.start_index, formula.start_index + 4)]
                    instance = cls(sequence, patterns=(formula.pattern_type,)
                                   if force_pattern else cls.DEFAULT_PATTERNS)
                except Exception as exc:
                    raise ValueError(
                        "The formula is not valid for generating a sequence.") from exc
            else:
                raise ValueError(
                    "The formula does not have an expression provided for calculation."
                )
        else:
            sequence = formula.calculate()
            instance = cls(sequence, patterns=(formula.pattern_type,)
                           if force_pattern else cls.DEFAULT_PATTERNS)
        return instance
