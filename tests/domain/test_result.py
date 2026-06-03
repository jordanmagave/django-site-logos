"""Testes para o tipo Result."""

from __future__ import annotations

import pytest

from src.domain.result import Error, Ok, error_result, ok_result


class TestOk:
    def test_is_ok(self) -> None:
        r = ok_result(42)
        assert r.is_ok()
        assert not r.is_error()

    def test_value_accessible(self) -> None:
        r = Ok("teste")
        assert r.value == "teste"

    def test_error_raises(self) -> None:
        r = ok_result("x")
        with pytest.raises(ValueError):
            _ = r.error


class TestError:
    def test_is_error(self) -> None:
        r = error_result("falhou")
        assert r.is_error()
        assert not r.is_ok()

    def test_error_accessible(self) -> None:
        r = Error("msg de erro")
        assert r.error == "msg de erro"

    def test_value_raises(self) -> None:
        r = error_result("erro")
        with pytest.raises(ValueError):
            _ = r.value


class TestFunctions:
    def test_ok_result(self) -> None:
        assert ok_result(1).value == 1

    def test_error_result(self) -> None:
        assert error_result("erro").error == "erro"
