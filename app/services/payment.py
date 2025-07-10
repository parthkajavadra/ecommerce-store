import stripe
from app.config import STRIPE_API_KEY
from app import models
from sqlalchemy.orm import Session

# Set up Stripe API key
stripe.api_key = STRIPE_API_KEY

def create_payment_intent(amount: float, currency: str = "usd") -> dict:
    """Create a payment intent for Stripe."""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe expects amount in cents
            currency=currency,
        )
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        }
    except Exception as e:
        raise Exception(f"Error creating payment intent: {str(e)}")


def confirm_payment(payment_intent_id: str, payment_method_id: str) -> dict:
    """Confirm a payment via Stripe."""
    try:
        payment_intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method=payment_method_id
        )
        return payment_intent
    except Exception as e:
        raise Exception(f"Error confirming payment: {str(e)}")


def update_order_status(order_id: int, status: str, db: Session) -> models.Order:
    """Update the order status in the database."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
        return order
    else:
        raise Exception(f"Order with ID {order_id} not found.")
