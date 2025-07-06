from fastapi.testclient import TestClient
from app.main import app  
from app.models import Order, OrderStatus
from app.database import SessionLocal

client = TestClient(app)

def test_cancel_order_processing():
    # Create an order with status "processing"
    db = SessionLocal()
    order = Order(user_id=1, total_price=100.0, status=OrderStatus.processing)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Send DELETE request to cancel the order
    response = client.delete(f"/orders/{order.id}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Order has been canceled successfully"
    
    # Verify status has changed to "canceled"
    updated_order = db.query(Order).filter(Order.id == order.id).first()
    assert updated_order.status == "canceled"

def test_prevent_cancel_order_shipped():
    # Create an order with status "shipped"
    db = SessionLocal()
    order = Order(user_id=1, total_price=100.0, status=OrderStatus.shipped)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Send DELETE request to cancel the order
    response = client.delete(f"/orders/{order.id}")
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot cancel an order that has already been shipped"

def test_get_order_canceled():
    # Create a canceled order manually (or via test case)
    db = SessionLocal()
    order = Order(user_id=1, total_price=100.0, status=OrderStatus.canceled)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Send GET request to fetch the canceled order
    response = client.get(f"/orders/{order.id}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "canceled"
