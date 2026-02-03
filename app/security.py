import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pin(pin: str) -> str:
    """
    Garante que o PIN nunca ultrapasse o limite do bcrypt (72 bytes)
    """
    if not pin:
        raise ValueError("PIN vazio não é permitido")

    pin = pin.strip()

    # HARD SAFETY — bcrypt limit
    if len(pin.encode("utf-8")) > 72:
        raise ValueError("PIN excede 72 bytes — verifique STRICT_STORE_PIN")

    return pwd_context.hash(pin)


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    if not plain_pin or not hashed_pin:
        return False

    plain_pin = plain_pin.strip()
    return pwd_context.verify(plain_pin, hashed_pin)
