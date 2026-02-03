import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext

# =====================
# CONFIG
# =====================
JWT_SECRET = os.getenv("JWT_SECRET", "brasa-secret-dev")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 12  # 12 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =====================
# PIN HASH
# =====================
def hash_pin(pin: str) -> str:
    return pwd_context.hash(pin)

def verify_pin(pin: str, pin_hash: str) -> bool:
    return pwd_context.verify(pin, pin_hash)

# =====================
# JWT TOKEN
# =====================
def create_token(store_id: int) -> str:
    payload = {
        "store_id": store_id,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("store_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
