from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, crud
from app.auth import get_current_user
from typing import List

router = APIRouter(prefix="/addresses", tags=["Addresses"])

# Create a new address
@router.post("/", response_model=schemas.Address)
def create_address(
    street: str,
    city: str,
    state: str,
    zip_code: str,
    country: str,
    phone_number: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new address."""
    address = crud.create_address(
        db=db,
        user_id=user.id,
        street=street,
        city=city,
        state=state,
        zip_code=zip_code,
        country=country,
        phone_number=phone_number
    )
    return address

# Get a single address by ID
@router.get("/{address_id}", response_model=schemas.Address)
def get_address(address_id: int, db: Session = Depends(get_db)):
    address = crud.get_address(db=db, address_id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

# Get all addresses for the current user
@router.get("/", response_model=List[schemas.Address])
def get_addresses(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    addresses = crud.get_addresses_by_user(db=db, user_id=user.id)
    return addresses

# Update an existing address
@router.put("/{address_id}", response_model=schemas.Address)
def update_address(
    address_id: int,
    street: str,
    city: str,
    state: str,
    zip_code: str,
    country: str,
    phone_number: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_address = crud.update_address(
        db=db,
        address_id=address_id,
        street=street,
        city=city,
        state=state,
        zip_code=zip_code,
        country=country,
        phone_number=phone_number
    )
    if not updated_address:
        raise HTTPException(status_code=404, detail="Address not found")
    return updated_address

# Delete an address
@router.delete("/{address_id}", response_model=schemas.Address)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    address = crud.delete_address(db=db, address_id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address
