import pytest
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError

from calculator_backend.routers import auth
from calculator_backend import schemas, models


class FakeQuery:
    def __init__(self, existing=None):
        self.existing = existing

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.existing


class FakeDB:
    def __init__(self, existing=None):
        self._query = FakeQuery(existing)
        self.added = None
        self.committed = False
        self.refreshed = None

    def query(self, model):
        return self._query

    def add(self, obj):
        self.added = obj

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed = obj
        # simulate DB assigning an id
        try:
            obj.id = 1
        except Exception:
            pass


def test_register_success_and_hash_called():
    user = schemas.UserCreate(username="newuser", password="secret")
    db = FakeDB(existing=None)

    with patch("calculator_backend.routers.auth.hash_password", return_value="hashedpwd") as mock_hash:
        result = auth.register(user, db)

        assert result == {"message": "User registered successfully"}
        # ensure DB add/commit/refresh were invoked (tracked on FakeDB)
        assert db.added is not None
        assert db.committed is True
        assert db.refreshed is db.added

        # ensure the created user model has expected values
        assert isinstance(db.added, models.User)
        assert db.added.username == "newuser"
        assert db.added.password_hash == "hashedpwd"

        # hashing called with the plain password
        mock_hash.assert_called_once_with("secret")


def test_register_duplicate_username_raises_400():
    user = schemas.UserCreate(username="existing", password="pw")#Input validation
    existing_user = models.User(username="existing", password_hash="h")#Database representation
    db = FakeDB(existing=existing_user)

    with pytest.raises(HTTPException) as excinfo:
        auth.register(user, db)

    assert excinfo.value.status_code == 400


def test_register_schema_validation_missing_fields():
    # missing password
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="onlyuser")

    # missing username
    with pytest.raises(ValidationError):
        schemas.UserCreate(password="onlypass")


def test_register_schema_validation_invalid_types():
    # invalid username type
    with pytest.raises(ValidationError):
        schemas.UserCreate(username=123, password="validpass")

    # invalid password type
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="validuser", password=123)

    # both invalid types
    with pytest.raises(ValidationError):
        schemas.UserCreate(username=123, password=456)
