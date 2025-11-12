from calculator_backend.utils.hashing import hash_password, verify_password


def test_hash_password_returns_non_empty_and_not_plain():
    plain = "s3cr3tP@ss"
    hashed = hash_password(plain)

    assert isinstance(hashed, str)
    assert len(hashed) > 0
    # bcrypt is salted, so hash should not equal the plain password
    assert hashed != plain


def test_verify_password_success_and_failure():
    plain = "mypassword"
    hashed = hash_password(plain)

    # correct password verifies
    assert verify_password(plain, hashed) is True

    # wrong password fails verification
    assert verify_password("wrongpass", hashed) is False



