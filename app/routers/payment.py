from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import models, schemas, payment
from app.database import get_db
from app.auth import get_current_user
from fastapi.responses import JSONResponse
import json


router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/create-payment-intent", response_model=schemas.PaymentIntentResponse)
def create_payment_intent(order_id: int, db: Session = Depends(get_db)):
    """Create a payment intent for the order."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order already paid or canceled")

    # Create payment intent with the total price
    response = payment.create_payment_intent(amount=order.total_price)
    
    return {"client_secret": response["client_secret"], "payment_intent_id": response["payment_intent_id"]}


@router.post("/confirm-payment", response_model=schemas.OrderResponse)
def confirm_payment(payment_intent_id: str, payment_method_id: str, order_id: int, db: Session = Depends(get_db)):
    """Confirm payment using Stripe."""
    # Confirm payment using Stripe
    payment_intent = payment.confirm_payment(payment_intent_id, payment_method_id)

    if payment_intent["status"] == "succeeded":
        # Update the order status to 'paid'
        updated_order = payment.update_order_status(order_id, "paid", db)
        return updated_order
    else:
        raise HTTPException(status_code=400, detail="Payment failed")

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')

    # Your Stripe webhook secret (get it from the Stripe dashboard)
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        
        # Handle the event (e.g., payment_intent.succeeded)
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent['metadata']['order_id']

            # Update the order status to 'paid'
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = "paid"
                db.commit()

            return JSONResponse({"status": "success"})
        
        else:
            return JSONResponse({"status": "unhandled event"})

    except ValueError as e:
        # Invalid payload
        return JSONResponse({"error": "Invalid payload"})
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JSONResponse({"error": "Invalid signature"})
