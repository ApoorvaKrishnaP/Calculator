from calculator_backend import database


class FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_get_db_calls_close(monkeypatch):
    fake = FakeSession()

    # patch SessionLocal to return our fake session
    monkeypatch.setattr(database, 'SessionLocal', lambda: fake)

    gen = database.get_db()
    sess = next(gen)
    assert sess is fake

    # closing the generator should trigger the finally block and close the session
    gen.close()
    assert fake.closed is True
