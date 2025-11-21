import main


def test_get_register_login_calculator_return_html():
    r = main.get_register()
    assert isinstance(r, str)
    assert len(r.strip()) > 0

    l = main.get_login()
    assert isinstance(l, str)
    assert len(l.strip()) > 0

    c = main.get_calculator()
    assert isinstance(c, str)
    assert len(c.strip()) > 0
