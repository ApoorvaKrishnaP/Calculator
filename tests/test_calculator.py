import pytest
from unittest.mock import patch
from fastapi import HTTPException
from calculator_backend.routers import calculator
from calculator_backend import schemas, models


class FakeQuery:
	def __init__(self, existing=None, all_results=None):
		self.existing = existing
		self._all = all_results or []

	def filter(self, *args, **kwargs):
		return self

	def first(self):
		return self.existing

	def all(self):
		return self._all


class FakeDB:
	def __init__(self, user=None, history=None):
		# user: models.User or None
		# history: list of models.History
		self._user = user
		self._history = history or []
		self.added = None
		self.committed = False

	def query(self, model):
		# Return a FakeQuery tailored to the requested model
		if model == models.User:
			return FakeQuery(existing=self._user)
		if model == models.History:
			return FakeQuery(all_results=self._history)
		return FakeQuery()

	def add(self, obj):
		self.added = obj

	def commit(self):
		self.committed = True


def make_user(username="alice", user_id=1):
	u = models.User(username=username, password_hash="h")
	try:
		u.id = user_id
	except Exception:
		pass
	return u


def make_history(user_id=1, expr="1+2", result="3"):
	h = models.History(user_id=user_id, expression=expr, result=result)
	try:
		h.id = 1
	except Exception:
		pass
	return h


def test_calculate_success_and_history_created():
	expr = schemas.Expression(expr="1+2")
	user = make_user(username="alice", user_id=5)
	db = FakeDB(user=user)

	with patch("calculator_backend.routers.calculator.verify_token", return_value="alice") as mock_verify:
		result = calculator.calculate(expr, Authorization="Bearer token", db=db)

		assert result["expression"] == "1+2"
		
		assert float(result["result"]) == pytest.approx(3.0)

		# verify DB side-effects
		assert isinstance(db.added, models.History)
		assert db.added.expression == "1+2"
		assert float(db.added.result) == pytest.approx(3.0)
		assert db.committed is True
		mock_verify.assert_called_once()


def test_calculate_invalid_token_raises_401():
	expr = schemas.Expression(expr="1+2")
	db = FakeDB(user=None)

	with patch("calculator_backend.routers.calculator.verify_token", return_value=None):
		with pytest.raises(HTTPException) as excinfo:
			calculator.calculate(expr, Authorization="Bearer bad", db=db)
		assert excinfo.value.status_code == 401


def test_calculate_invalid_expression_raises_400():
    expr = schemas.Expression(expr="1/0")
    user = make_user(username="alice")
    db = FakeDB(user=user)

    with patch("calculator_backend.routers.calculator.verify_token", return_value="alice"):
        with pytest.raises(HTTPException) as excinfo:
            calculator.calculate(expr, Authorization="Bearer tok", db=db)
        assert excinfo.value.status_code == 400
        # assert "Invalid Expression" in str(excinfo.value.detail)


def test_get_history_success_returns_list():
	user = make_user(username="bob", user_id=7)
	history_items = [make_history(user_id=7, expr="2+2", result="4"), make_history(user_id=7, expr="3+3", result="6")]
	db = FakeDB(user=user, history=history_items)

	with patch("calculator_backend.routers.calculator.verify_token", return_value="bob"):
		records = calculator.get_history(Authorization="Bearer tok", db=db)
		assert isinstance(records, list)
		assert len(records) == 2
		assert records[0].expression == "2+2"


def test_get_history_empty_returns_empty_list():
	user = make_user(username="carol", user_id=8)
	db = FakeDB(user=user, history=[])

	with patch("calculator_backend.routers.calculator.verify_token", return_value="carol"):
		records = calculator.get_history(Authorization="Bearer tok", db=db)
		assert records == []


def test_get_history_invalid_token_raises_401():
	db = FakeDB(user=None, history=[])
	with patch("calculator_backend.routers.calculator.verify_token", return_value=None):
		with pytest.raises(HTTPException) as excinfo:
			calculator.get_history(Authorization="Bearer bad", db=db)
		assert excinfo.value.status_code == 401
#except sp.SympifyError:
    #raise Exception("Invalid Expression entered")
