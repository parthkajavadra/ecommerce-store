from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from fastapi import APIRouter
from typing import List
from app.utils import generate_invoice_pdf
from app.email import send_invoice_email
from app.schemas import Order, OrderItem
from app.models import Order as OrderModel, OrderItem as OrderItemModel


router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/orders")
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_price = 0
    order_items = []

    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        item_price = product.price
        total_price += item_price * item.quantity

        order_items.append(models.OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price=item_price
        ))
    new_order = models.Order(user_id=current_user.id, total_price=total_price)
    db.add(new_order)
    db.flush()
    for item in order_items:
        item.order_id = new_order.id
        db.add(item)

    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "total_price": total_price
    }

@router.get("/orders", response_model=List[schemas.OrderSummary])
def list_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    orders = db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders


@router.get("/orders/{order_id}", response_model=schemas.OrderDetail)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order_items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
    order_detail = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "created_at": order.created_at,
        "status": order.status,
        "payment_status": order.payment_status,
        "shipping_status": order.shipping_status,
        "items": [
            schemas.OrderItemDetail(
                product_id=item.product.id,
                product_name=item.product.name,  # Automatically fetch product name from the related product
                quantity=item.quantity,
                price=item.price
            )
            for item in order_items
        ]
    }
    
    return order_detail

@router.delete("/orders/{order_id}", response_model=schemas.OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status in ["shipped", "delivered"]:
        raise HTTPException(status_code=400, detail="Cannot cancel a shipped or delivered order")

    order.status = "canceled"
    db.commit()
    db.refresh(order)

    return order

@router.put("/orders/{order_id}/status", response_model=schemas.OrderStatusUpdate)
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update status fields
    if status_update.status:
        order.status = status_update.status
    if status_update.payment_status:
        order.payment_status = status_update.payment_status
    if status_update.shipping_status:
        order.shipping_status = status_update.shipping_status

    db.commit()
    db.refresh(order)

    return { "message": "Order status updated successfully" }

@router.put("/update_status/{order_id}")
def update_order_status(
    order_id: int, status: str, 
    tracking_number: str = None, 
    shipping_carrier: str = None, 
    db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)
):
    """Update the status and tracking information for an order"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order status
    order.status = status
    if tracking_number:
        order.tracking_number = tracking_number
    if shipping_carrier:
        order.shipping_carrier = shipping_carrier

    db.commit()
    db.refresh(order)
    return {"msg": "Order status updated successfully", "order": order}

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order_status(order_id: int, db: Session = Depends(get_db)):
    """Get order status and tracking information"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.post("/generate_invoice/{order_id}", response_model=Order)
def generate_invoice(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order_items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
    pdf_invoice = generate_invoice_pdf(order, order_items)  # Pass both order and order_items

    # Assuming you save the generated PDF or return it as part of the response
    # For example, you can store the PDF in the database or return it as a base64 string.

    # Return the order data along with its items
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "shipping_address": order.shipping_address,
        "total_amount": order.total_price,
        "items": [{"product_name": item.product_name, "quantity": item.quantity, "price": item.price} for item in order_items]
    }