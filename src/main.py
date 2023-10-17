from datetime import datetime, timedelta
from typing import Annotated, Union

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import HTMLResponse

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)

templates = Jinja2Templates(directory="templates")

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

def get_db(request: Request):
    return request.state.db

@app.post("/users/", response_model=schemas.User)
def create_user( user: schemas.UserCreate, db: Session = Depends(get_db) ):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users( 
    skip: int = 0, 
    limit: int = 100, 
    db : Session = Depends(get_db) ):
    users = crud.get_user(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return db_user

@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int,
    item: schemas.ItemCreate,
    db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)

@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


#def get_current_user_from_token(token: str = Depends(oau))


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    #return FileResponse('./templates/home.html')

    return templates.TemplateResponse(
            "home.html", {"request": request}
        )

@app.get("/login")
def login(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
        }
    )



































# ##########################################################################

# SECRET_KEY = "22364cdf4ea5e5ec150ee30d9ae7f8506f9d1b587a44a58a970a79077cf18ec2"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
#         "disabled": False,
#     }
# }
# class User(BaseModel):
#     username: str
#     email: Union[str, None] = None
#     full_name: Union[str, None] = None
#     disabled: Union[bool, None] = None

# class UserInDB(User):
#     hashed_password : str


# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: Union[str, None] = None

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def fake_decode_token(token):
#     # return User(
#     #     username=token + "fakedecode",
#     #     email="harsh@example.com",
#     #     full_name="Harsh joon"
#     # )
#     user = get_user(fake_users_db, token)
#     return user

# def fake_hash_password( password:str):
#     return "fakehashed" + password

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)
    
# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     # user = fake_decode_token(token)
#     # return user

#     # user = fake_decode_token(token)
#     # if not user:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_401_UNAUTHORIZED,
#     #         detail="Invalid authentication credentials",
#     #         headers={"WWW-Authenticate": "Bearer"},
#     #     )
#     # return user

#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"}
#     )

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
    
#     user = get_user(fake_users_db, username= token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user

# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]    
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# @app.post("/token", response_model=Token)
# async def login(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ):
#     user = authenticate_user(
#         fake_users_db,
#         form_data.username,
#         form_data.password
#     )
#     if not user:
#         HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"}
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token         = create_access_token(
#         data={
#             "sub": user.username
#         },
#         expires_delta=access_token_expires
#     )

#     return {
#         "access_token": access_token,
#         "token_type"  : "bearer"
#     }

#     # user_dict = fake_users_db.get(form_data.username)
#     # if not user_dict:
#     #     raise HTTPException(
#     #         status_code=400,
#     #         detail="Incorrect username or password"
#     #     )
#     # user = UserInDB(**user_dict)
#     # hashed_password = fake_hash_password(form_data.password)
#     # if not hashed_password == user.hashed_password:
#     #     raise HTTPException(
#     #         status_code=400,
#     #         detail="Incorrect username or password"
#     #     )
#     # return {
#     #     "access_token": user.username,
#     #     "token_type"  : "bearer"
#     # }

# @app.get("/users/me", response_model=User)
# async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
#     return current_user


# @app.get("/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[User, Depends(get_current_active_user)]
# ):
#     return [{
#         "item_id": "Foo",
#         "owner"  : current_user.username
#     }]

# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}

# ##########################################################################