from typing         import Union
from pydantic       import BaseModel
from typing         import Optional

class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None

class ItemCreate(ItemBase):
    pass 

class Item(ItemBase):
    id: Optional[int] = None
    owner_id: Optional[int] = None
    class Config:
        orm_model = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int = 0
    is_active: Optional[bool] = None
    items: Optional[list[Item]] = None
    class Config:
        orm_mode = True


