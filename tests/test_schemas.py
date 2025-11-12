import pytest
from pydantic import ValidationError

from calculator_backend.schemas import UserCreate, Expression, Token


def test_usercreate_valid_and_invalid():
    uc = UserCreate(username='alice', password='s3cr3t')
    assert uc.username == 'alice'

    with pytest.raises(ValidationError):
        UserCreate(username='onlyuser')  # missing password

    with pytest.raises(ValidationError):
        UserCreate(password='onlypass')  # missing username

    with pytest.raises(ValidationError):
        UserCreate(username=123, password='pw')  # wrong type


def test_expression_validation():
    e = Expression(expr='1+1')
    assert e.expr == '1+1'

    with pytest.raises(ValidationError):
        Expression(expr=123)  # wrong type
