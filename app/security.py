from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pin(pin: str) -> str:
    pin = pin.strip()

    if len(pin.encode("utf-8")) > 72:
        raise ValueError("PIN maior que 72 bytes. Verifique variável de ambiente.")

    return pwd_context.hash(pin)
