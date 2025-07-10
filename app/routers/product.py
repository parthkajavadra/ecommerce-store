from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.dependencies import require_roles
from app.models import UserRole, User

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=schemas.ProductPaginationResponse)
def get_products(
    db: Session = Depends(get_db),
    page: int = Query(1, alias="page", ge=1),  # Default to page 1
    page_size: int = Query(10, alias="page_size", ge=1),  # Default to 10 items per page
    search: str = Query(None, max_length=50),
    min_price: float = Query(None, gt=0),
    max_price: float = Query(None, gt=0)
):
    query = db.query(models.Product)
    
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    if min_price:
        query = query.filter(models.Product.price >= min_price)
    if max_price:
        query = query.filter(models.Product.price <= max_price)

    total_count = query.count()

    products = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {"products": products, "total_count": total_count}

# @router.get("/", response_model=list[schemas.Product])
# def list_products(db: Session = Depends(get_db)):
#     return db.query(models.Product).all()

# @router.get("/{product_id}", response_model=schemas.Product)
# def get_product(product_id: int, db: Session = Depends(get_db)):
#     product = db.query(models.Product).get(product_id)
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product

@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SELLER))
):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    updated: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(UserRole.ADMIN))
):
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in updated.dict().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(UserRole.ADMIN))
):
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
