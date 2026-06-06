from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.API_layer.security import create_access_token, verify_password, get_password_hash
from pydantic import BaseModel
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Mock database για εκπαιδευτικούς σκοπούς
MOCK_USER = {
    "username": "compliance_officer",
    "hashed_password": get_password_hash("accenture2026") # Password: accenture2026
}

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != MOCK_USER["username"] or not verify_password(form_data.password, MOCK_USER["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}