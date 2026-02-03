import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

# =====================
# CONFIG
# =====================
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 12  # 12 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =====================
# PIN SECURITY
# =====================
def hash_pin(pin: str) -> str:
    """
    Garante que o PIN nunca ultrapasse o limite do bcrypt (72 bytes)
    """
    if not pin:
        raise ValueError("PIN vazio não é permitido")

    pin = pin.strip()

    if len(pin.encode("utf-8")) > 72:
        raise ValueError("PIN excede 72 bytes — verifique STRICT_STORE_PIN")

    return pwd_context.hash(pin)


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    if not plain_pin or not hashed_pin:
        return False

    plain_pin = plain_pin.strip()
    return pwd_context.verify(plain_pin, hashed_pin)

# =====================
# JWT SECURITY
# =====================
def create_token(store_id: int, store_name: str) -> str:
    payload = {
        "store_id": store_id,
        "store_name": store_name,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
