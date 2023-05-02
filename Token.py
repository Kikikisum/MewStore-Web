import time
import jwt

#  密钥
SECRET_KEY: str = "mewstore"
#  加密算法
ALGORITHM = "HS256"


def get_id(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: int = payload.get("id")
        return uid
    except Exception as e:
        print(e)


def get_status(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        status: int = payload.get("status")
        return status
    except Exception as e:
        print(e)


def get_expiration(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiration = int(payload.get("exp"))
        if time.time() > expiration:
            return False
        else:
            return True
    except Exception as e:
        print(e)







