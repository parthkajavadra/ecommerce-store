from sqlalchemy.orm import Session
from app import models

# Create a new address
def create_address(
    db: Session,
    user_id: int,
    street: str,
    city: str,
    state: str,
    zip_code: str,
    country: str,
    phone_number: str,
    is_default: bool = False
):
    db_address = models.Address(
        user_id=user_id,
        street=street,
        city=city,
        state=state,
        zip_code=zip_code,
        country=country,
        phone_number=phone_number,
        is_default=is_default
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

# Get an address by ID
def get_address(db: Session, address_id: int):
    return db.query(models.Address).filter(models.Address.id == address_id).first()

# Get all addresses by user ID
def get_addresses_by_user(db: Session, user_id: int):
    return db.query(models.Address).filter(models.Address.user_id == user_id).all()

# Update an address
def update_address(
    db: Session,
    address_id: int,
    street: str,
    city: str,
    state: str,
    zip_code: str,
    country: str,
    phone_number: str,
    is_default: bool = False
):
    db_address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if db_address:
        db_address.street = street
        db_address.city = city
        db_address.state = state
        db_address.zip_code = zip_code
        db_address.country = country
        db_address.phone_number = phone_number
        db_address.is_default = is_default
        db.commit()
        db.refresh(db_address)
    return db_address

# Delete an address
def delete_address(db: Session, address_id: int):
    db_address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if db_address:
        db.delete(db_address)
        db.commit()
    return db_address
