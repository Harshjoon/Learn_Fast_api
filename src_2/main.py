from fastapi import (
    Depends, 
    FastAPI, 
    HTTPException, 
    Request, 
    Response,
    Form,
    status    
)

from sqlalchemy.orm     import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sql_app           import crud, models, schemas
from sql_app.database  import SessionLocal, engine

from pathlib import Path

app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)

templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internel server error", status_code=500)
    try:
        request.state.db    = SessionLocal()
        response            = await call_next(request)
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
    skip: int=0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    users = crud.get_users(db, skip=skip, limit=limit)
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
    #return None

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

# HTML RESPONSES
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
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

def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    user = db.query(models.User).filter(models.User.email == email).first()

    from auth.auth import verify_password

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request,db: Session = Depends(get_db)):
    from auth.login import LoginForm
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("private", status.HTTP_302_FOUND)

            '''
            TODO
            - Find user if exists
            - Check password if user exists
            - Throw error if invalid.
            '''
            if authenticate_user(db, form.username, form.password):
                return response
            else:
                raise HTTPException(409, detail='Error raised')
            
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


@app.get("/private")
def login(request: Request):
    return templates.TemplateResponse(
        "private_home.html",
        {
            "request": request,
        }
    )