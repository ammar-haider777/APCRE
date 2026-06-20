# -*- coding: utf-8 -*-
"""User repository implementing clean data access layer."""


class User:
    """Domain entity representing an application user."""

    def __init__(self, user_id: int, username: str, email: str) -> None:
        self._user_id: int = user_id
        self._username: str = username
        self._email: str = email

    @property
    def user_id(self) -> int:
        """Return the immutable user identifier."""
        return self._user_id

    @property
    def username(self) -> str:
        """Return the username."""
        return self._username

    @property
    def email(self) -> str:
        """Return the user email address."""
        return self._email

    def __repr__(self) -> str:
        return f"User(id={self._user_id}, username={self._username!r})"


class UserRepository:
    """In-memory repository with proper encapsulation and type hints."""

    def __init__(self) -> None:
        self._store: dict[int, User] = {}

    def add(self, user: User) -> None:
        """Persist a user entity."""
        if not isinstance(user, User):
            raise TypeError("Expected a User instance.")
        self._store[user.user_id] = user

    def find_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by primary key."""
        return self._store.get(user_id)

    def list_all(self) -> list[User]:
        """Return all stored users."""
        return list(self._store.values())

    def count(self) -> int:
        """Return the total number of persisted users."""
        return len(self._store)
