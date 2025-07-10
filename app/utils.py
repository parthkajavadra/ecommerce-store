import weasyprint
from io import BytesIO
from app.models import Order, OrderItem

def generate_invoice_pdf(order: Order, order_items: list) -> BytesIO:
    """Generate an invoice PDF for the given order."""
    
    # Create an HTML template for the invoice
    html_content = f"""
    <html>
    <body>
        <h1>Invoice for Order #{order.id}</h1>
        <p>Status: {order.status}</p>
        <p>Total Price: ${order.total_price}</p>
        
        <h3>Order Items:</h3>
        <table border="1">
            <tr>
                <th>Product Name</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
            {''.join(f"<tr><td>{item.product.name}</td><td>{item.quantity}</td><td>${item.price}</td><td>${item.price * item.quantity}</td></tr>" for item in order_items)}
        </table>
        
        <h3>Total Price: ${order.total_price}</h3>
    </body>
    </html>
    """
    
    # Convert HTML to PDF using WeasyPrint
    pdf = weasyprint.HTML(string=html_content).write_pdf()

    # Return the PDF as a BytesIO object
    return BytesIO(pdf)
