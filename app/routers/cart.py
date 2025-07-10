from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
import redis
import json

router = APIRouter(prefix="/cart", tags=["Cart"])

# Redis connection setup (adjust the Redis host/port as needed)
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_or_create_cart(user: models.User, db: Session) -> models.Cart:
    """Get or create a cart for logged-in users."""
    cart = db.query(models.Cart).filter(models.Cart.user_id == user.id).first()
    if not cart:
        cart = models.Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def get_or_create_guest_cart(session_id: str) -> dict:
    """Get or create a cart for guest users using Redis."""
    cart = r.get(session_id)
    if not cart:
        cart = {}
        r.set(session_id, json.dumps(cart))  # Initialize empty cart for guest user
    else:
        cart = json.loads(cart)
    return cart

def merge_cart_from_redis(user: models.User, db: Session, session_id: str) -> models.Cart:
    """Merge the guest cart (from Redis) into the logged-in user's cart."""
    guest_cart = get_or_create_guest_cart(session_id)

    cart = get_or_create_cart(user, db)

    # Merge items into the user's cart from Redis
    for product_id, quantity in guest_cart.items():
        # Check if the product is already in the user's cart
        cart_item = db.query(models.CartItem).filter(
            models.CartItem.cart_id == cart.id,
            models.CartItem.product_id == product_id
        ).first()

        if cart_item:
            cart_item.quantity += quantity  # Update quantity if already exists
        else:
            # Add new item to the user's cart
            db_item = models.CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(db_item)

    db.commit()
    db.refresh(cart)
    
    # Clear the guest cart from Redis after merging
    r.delete(session_id)

    return cart

@router.get("/", response_model=schemas.Cart)
def get_cart(user: models.User = Depends(get_current_user), db: Session = Depends(get_db), session_id: str = None):
    """Get the cart for logged-in users or merge guest cart if not logged in."""
    if user:
        # For logged-in users, get the DB cart
        cart = get_or_create_cart(user, db)
        return cart
    elif session_id:
        # For guest users, get the Redis cart
        cart = get_or_create_guest_cart(session_id)
        return {"items": cart}  # Return cart items for guests
    else:
        raise HTTPException(status_code=400, detail="No session found for guest.")

@router.post("/add", response_model=schemas.Cart)
def add_to_cart(item: schemas.CartItemCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db), session_id: str = None):
    """Add an item to the cart for both logged-in users and guest users."""
    if user:
        cart = get_or_create_cart(user, db)
        existing_item = db.query(models.CartItem).filter(
            models.CartItem.cart_id == cart.id,
            models.CartItem.product_id == item.product_id
        ).first()

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
    elif session_id:
        guest_cart = get_or_create_guest_cart(session_id)
        guest_cart[item.product_id] = guest_cart.get(item.product_id, 0) + item.quantity
        r.set(session_id, json.dumps(guest_cart))
        return {"message": "Item added to guest cart."}
    else:
        raise HTTPException(status_code=400, detail="No session found for guest.")

@router.put("/update", response_model=schemas.Cart)
def update_quantity(item: schemas.CartItemCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db), session_id: str = None):
    """Update the quantity of an item in the cart."""
    if user:
        cart = get_or_create_cart(user, db)

        cart_item = db.query(models.CartItem).filter(
            models.CartItem.cart_id == cart.id,
            models.CartItem.product_id == item.product_id
        ).first()

        if not cart_item:
            raise HTTPException(status_code=404, detail="Item not in cart")

        cart_item.quantity = item.quantity
        db.commit()
        db.refresh(cart)
        return cart
    elif session_id:
        guest_cart = get_or_create_guest_cart(session_id)
        if item.product_id not in guest_cart:
            raise HTTPException(status_code=404, detail="Item not in guest cart")

        guest_cart[item.product_id] = item.quantity
        r.set(session_id, json.dumps(guest_cart))
        return {"message": "Guest cart updated."}
    else:
        raise HTTPException(status_code=400, detail="No session found for guest.")

@router.delete("/remove/{product_id}", response_model=schemas.Cart)
def remove_item(product_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db), session_id: str = None):
    """Remove an item from the cart."""
    if user:
        cart = get_or_create_cart(user, db)

        cart_item = db.query(models.CartItem).filter(
            models.CartItem.cart_id == cart.id,
            models.CartItem.product_id == product_id
        ).first()

        if not cart_item:
            raise HTTPException(status_code=404, detail="Item not found")

        db.delete(cart_item)
        db.commit()
        db.refresh(cart)
        return cart
    elif session_id:
        guest_cart = get_or_create_guest_cart(session_id)
        if product_id not in guest_cart:
            raise HTTPException(status_code=404, detail="Item not found in guest cart")

        del guest_cart[product_id]
        r.set(session_id, json.dumps(guest_cart))
        return {"message": "Item removed from guest cart."}
    else:
        raise HTTPException(status_code=400, detail="No session found for guest.")
