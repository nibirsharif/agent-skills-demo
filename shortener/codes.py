"""Short code generation."""

import secrets
import string

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6


def new_code(length=CODE_LENGTH):
    """Return a random code of letters and digits."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
