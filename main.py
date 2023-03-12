from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter
from sqlalchemy import Column, Boolean, String
from sqlalchemy.ext.asyncio  import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import settings
from sqlalchemy.dialects.postgresql import UUID
import uuid
import re
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import validator


############################################
# BLOCK FOR COMMON INTERACTION WITH DATABASE
############################################

#create asyng engine for interaction with database
#создаём асинхронный движок для взаимодействия с бд
engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

#create session for interaction with database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


##########################
#BLOCK WITH DATABASE MODEL
##########################

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid1())
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default= True)

########################################################
#BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT
########################################################

class UserDAL:
    '''Data Access Layer for operating user info'''
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
            self, name: str, surname: str, email: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

#######################
# BLOCK WITH API MODELS
#######################

LETTER_MATCH_PATTERN = re.compile(r'^[а-яА-Яa-zA-Z\-+]-$')

class TuneModel(BaseModel):
    class Config:
        '''tells to pydantic to convert even non dict obj to json'''

        orm_mode = True

class ShowUser(TuneModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool

class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr

    @validator('name'):
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Name should contains only letters'
            )
        return value

    @validator('surname'):
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Surname should contains only letters'
            )
        return value















# if __name__ == '__main__':
#     print_hi('PyCharm')


