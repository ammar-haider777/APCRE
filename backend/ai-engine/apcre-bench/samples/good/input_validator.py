# -*- coding: utf-8 -*-
"""Input validation utilities following the Single Responsibility Principle."""

import re


class ValidationResult:
    """Immutable result of a validation check."""

    def __init__(self, is_valid: bool, message: str = "") -> None:
        self._is_valid: bool = is_valid
        self._message: str = message

    @property
    def is_valid(self) -> bool:
        """Whether the validation passed."""
        return self._is_valid

    @property
    def message(self) -> str:
        """Human-readable validation message."""
        return self._message


class EmailValidator:
    """Validates email addresses using a compiled regex pattern."""

    _PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def validate(self, email: str) -> ValidationResult:
        """Check whether *email* conforms to a valid email format."""
        if not email or not isinstance(email, str):
            return ValidationResult(False, "Email must be a non-empty string.")
        if self._PATTERN.match(email):
            return ValidationResult(True, "Valid email address.")
        return ValidationResult(False, f"Invalid email format: {email!r}")


class PasswordValidator:
    """Enforces minimum password strength requirements."""

    MIN_LENGTH: int = 8

    def validate(self, password: str) -> ValidationResult:
        """Ensure *password* meets strength criteria."""
        if len(password) < self.MIN_LENGTH:
            return ValidationResult(
                False, f"Password must be at least {self.MIN_LENGTH} characters."
            )
        if not re.search(r"[A-Z]", password):
            return ValidationResult(False, "Password must contain an uppercase letter.")
        if not re.search(r"[0-9]", password):
            return ValidationResult(False, "Password must contain a digit.")
        return ValidationResult(True, "Password meets strength requirements.")
