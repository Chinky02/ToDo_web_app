from fastapi import FastAPI, Depends, APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import or_

import bcrypt

from database import get_db
from models.models import User

router = APIRouter()


class AddUser(BaseModel):
    first_name:str
    middle_name:Optional[str] = None
    last_name:str
    email:str
    phone_number:str
    password:str

class LoginUser(BaseModel):
    email:Optional[str] = None
    phone_number:Optional[str] = None
    password:str

class UserClass:
    def __init__(self, db):
        self.db = db
    
    def hash_password(self, plain_text_password: str) -> str:
        return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_text_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def add_user(self, details:AddUser):
        try:
            check_user = self.db.query(User).filter(or_(User.email==details.email, User.phone_number == details.phone_number)).first()
            if check_user:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                                    content={"message": "User already exists"})
            
            user_details = User(
                first_name=details.first_name.lower(),
                middle_name=details.middle_name,
                last_name=details.last_name.lower(),
                full_name=f"{details.first_name} {details.middle_name} {details.last_name}".lower(),
                email=details.email.lower(),
                phone_number=details.phone_number,
                password=self.hash_password(details.password)
            )

            self.db.add(user_details)
            self.db.commit()
            self.db.close()

            return JSONResponse(status_code=status.HTTP_201_CREATED, 
                                content={"message": "User created successfully"})
        except Exception as e:
            self.db.close()
            print(e)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content={"message": "Internal Server Error"})
        
    
    def login_user(self, details:LoginUser):
        try:
            if not details.email and not details.phone_number:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                                    content={"message": "Email or Phone Number is required"})
            if details.email:
                user = self.db.query(User).filter(User.email==details.email).first()
                if not user:
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                                        content={"message": "Invalid Email. Please try again."})
            if details.phone_number:
                user = self.db.query(User).filter(User.phone_number ==details.phone_number).first()
                if not user:
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                                        content={"message": "Invalid Phone Number. Please try again."})
            if not self.verify_password(details.password, user.password):
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, 
                                    content={"message": "Invalid Password. Please try again."})
            return JSONResponse(status_code=status.HTTP_200_OK, 
                                content={"message": "Login successful", "user": user.id})
        except Exception as e:
            print(e)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content={"message": "Internal Server Error"})

@router.post("/add-user")
async def add_user(details:AddUser, db = Depends(get_db)):
    response = UserClass(db=db).add_user(details=details)
    return response

@router.post("/login")
async def login(details:LoginUser, db = Depends(get_db)):
    response = UserClass(db=db).login_user(details=details)
    return response
