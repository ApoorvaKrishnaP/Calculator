from calculator_backend import models


def test_models_attributes_and_instantiation():
    # tablenames
    assert hasattr(models.User, '__tablename__')
    assert models.User.__tablename__ == 'users'
    assert hasattr(models.History, '__tablename__')
    assert models.History.__tablename__ == 'history'

    # instantiate and check attributes
    u = models.User(username='testuser', password_hash='h')
    assert u.username == 'testuser'
    assert u.password_hash == 'h'

    h = models.History(user_id=1, expression='2+3', result='5')
    assert h.expression == '2+3'
    assert h.result == '5'

    # relationships exist on class
    assert hasattr(models.User, 'calculations')
    assert hasattr(models.History, 'user')
