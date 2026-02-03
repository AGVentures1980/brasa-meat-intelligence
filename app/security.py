import os
from passlib.context import CryptContext

# Força backend bcrypt puro (evita bug de __about__ no Render)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

MAX_BCRYPT_BYTES = 72


def _normalize_pin(pin: str) -> str:
    if not pin:
        raise ValueError("PIN vazio não é permitido")
    return pin.strip()


def hash_pin(pin: str) -> str:
    """
    Gera hash seguro para PIN da loja
    Protege contra limite de 72 bytes do bcrypt
    """
    pin = _normalize_pin(pin)

    if len(pin.encode("utf-8")) > MAX_BCRYPT_BYTES:
        raise ValueError("PIN excede 72 bytes — verifique STRICT_STORE_PIN no Render")

    return pwd_context.hash(pin)


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """
    Verifica PIN digitado contra hash armazenado
    Nunca lança exceção — falha com False
    """
    try:
        plain_pin = _normalize_pin(plain_pin)
        return pwd_context.verify(plain_pin, hashed_pin)
    except Exception:
        return False
