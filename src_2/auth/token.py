from datetime           import datetime, timedelta
from typing             import Annotated, Union

from fastapi            import (
    Depends,
    HTTPException,
    status,
    Request,
)
from jose               import JWTError, jwt
from passlib.context    import CryptContext
from pydantic           import BaseModel

from sqlalchemy         import Session

class Token(BaseModel):
    access_token    : str
    token_type      : str

class TokenData(BaseModel):
    username        : Union[str, None] = None

from sql_app            import models
from auth.auth          import oauth2_scheme


def get_db(request: Request):
    return request.state.db

def create_access_token(
        data: dict,
        expires_delta: Union[timedelta, None] = None
        ):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    from auth.auth import SECRET_KEY, ALGORITHM
    encoded_jwt     = jwt.encode(to_encode, SECRET_KEY, algorithm=[ALGORITHM])
    return encoded_jwt

async def get_current_user(        
        token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    from auth.auth          import SECRET_KEY, ALGORITHM
    try:
        payload         = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str  = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data      = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    from sql_app.crud import get_user_by_email

    db: Session = Depends(get_db)
    user                = get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


