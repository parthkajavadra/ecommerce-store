from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_or_create_cart(user: models.User, db: Session) -> models.Cart:
    cart = db.query(models.Cart).filter(models.Cart.user_id == user.id).first()
    if not cart:
        cart = models.Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.get("/", response_model=schemas.Cart)
def get_cart(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)
    return cart

@router.post("/add", response_model=schemas.Cart)
def add_to_cart(item: schemas.CartItemCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)

    existing_item = (
        db.query(models.CartItem)
        .filter(models.CartItem.cart_id == cart.id, models.CartItem.product_id == item.product_id)
        .first()
    )

    if existing_item:
        existing_item.quantity += item.quantity
    else:
        db_item = models.CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(db_item)

    db.commit()
    db.refresh(cart)
    return cart

@router.put("/update", response_model=schemas.Cart)
def update_quantity(item: schemas.CartItemCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)

    cart_item = (
        db.query(models.CartItem)
        .filter(models.CartItem.cart_id == cart.id, models.CartItem.product_id == item.product_id)
        .first()
    )

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    cart_item.quantity = item.quantity
    db.commit()
    db.refresh(cart)
    return cart

@router.delete("/remove/{product_id}", response_model=schemas.Cart)
def remove_item(product_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)

    cart_item = (
        db.query(models.CartItem)
        .filter(models.CartItem.cart_id == cart.id, models.CartItem.product_id == product_id)
        .first()
    )

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(cart_item)
    db.commit()
    db.refresh(cart)
    return cart
