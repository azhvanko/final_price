import argon2

__all__ = (
    "hash_password",
    "verify_password",
)

ph: argon2.PasswordHasher = argon2.PasswordHasher.from_parameters(argon2.profiles.RFC_9106_LOW_MEMORY)


def hash_password(raw_password: str) -> str:
    return ph.hash(raw_password)


def verify_password(hash: str, raw_password: str) -> bool:
    try:
        return ph.verify(hash, raw_password)
    except argon2.exceptions.VerificationError:
        return False
