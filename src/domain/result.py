"""Tipo Result para retorno de operações que podem falhar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    _value: T
    _is_ok: bool = True

    def is_ok(self) -> bool:
        return True

    def is_error(self) -> bool:
        return False

    @property
    def value(self) -> T:
        return self._value

    @property
    def error(self) -> str:
        raise ValueError("Ok result has no error")


@dataclass(frozen=True, slots=True)
class Error(Generic[T]):
    _error: str
    _is_ok: bool = False

    def is_ok(self) -> bool:
        return False

    def is_error(self) -> bool:
        return True

    @property
    def error(self) -> str:
        return self._error

    @property
    def value(self) -> T:
        raise ValueError("Error result has no value")


Result = Ok[T] | Error[T]


def ok_result(value: T) -> Result[T]:
    return Ok(value)


def error_result(msg: str) -> Result[T]:
    return Error(msg)
