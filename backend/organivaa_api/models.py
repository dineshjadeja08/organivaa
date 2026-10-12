from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Operator(Base):
    __tablename__ = "operators"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="owner")
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Record(Base):
    __tablename__ = "operation_records"
    __table_args__ = (UniqueConstraint("resource", "external_id", name="uq_resource_external_id"), Index("ix_record_resource_status", "resource", "status"))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource: Mapped[str] = mapped_column(String(40), index=True)
    external_id: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(24), default="draft")
    value: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payload: Mapped[str] = mapped_column(Text, default="{}")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(255), default="next-admin")
    action: Mapped[str] = mapped_column(String(40))
    resource: Mapped[str] = mapped_column(String(40))
    record_id: Mapped[str] = mapped_column(String(80))
    summary: Mapped[str] = mapped_column(String(500))
    before: Mapped[str | None] = mapped_column(Text, nullable=True)
    after: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_record_id: Mapped[int] = mapped_column(ForeignKey("operation_records.id", ondelete="CASCADE"), index=True)
    sku: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price_paise: Mapped[int] = mapped_column(Integer)
    order: Mapped[Record] = relationship()


class CatalogProduct(Base):
    __tablename__ = "catalog_products"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    handle: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    ingredient: Mapped[str] = mapped_column(String(120), index=True)
    format: Mapped[str] = mapped_column(String(80), index=True)
    concern: Mapped[str] = mapped_column(String(120), index=True)
    origin: Mapped[str] = mapped_column(String(255), default="Verification pending")
    ritual: Mapped[str] = mapped_column(String(120), default="Follow pack directions")
    badge: Mapped[str | None] = mapped_column(String(80), nullable=True)
    accent: Mapped[str] = mapped_column(String(80), default="botanical")
    primary_image: Mapped[str] = mapped_column(String(500), default="/images/organivaa-hero-branded.png")
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
    seo_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    variants: Mapped[list["ProductVariant"]] = relationship(back_populates="product", cascade="all, delete-orphan", order_by="ProductVariant.position")
    assets: Mapped[list["Asset"]] = relationship(back_populates="product", cascade="all, delete-orphan", order_by="Asset.position")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id: Mapped[str] = mapped_column(ForeignKey("catalog_products.id", ondelete="CASCADE"), index=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(160))
    detail: Mapped[str] = mapped_column(String(255), default="")
    pack_size: Mapped[str] = mapped_column(String(80))
    servings: Mapped[int] = mapped_column(Integer, default=1)
    price_paise: Mapped[int] = mapped_column(Integer)
    mrp_paise: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(24), default="active")
    product: Mapped[CatalogProduct] = relationship(back_populates="variants")


class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id: Mapped[str | None] = mapped_column(ForeignKey("catalog_products.id", ondelete="CASCADE"), nullable=True, index=True)
    original_name: Mapped[str] = mapped_column(String(255))
    filename: Mapped[str] = mapped_column(String(255), unique=True)
    mime_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(40), default="image")
    alt_text: Mapped[str] = mapped_column(String(255), default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    product: Mapped[CatalogProduct | None] = relationship(back_populates="assets")


class CommerceOrder(Base):
    __tablename__ = "commerce_orders"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    subtotal_paise: Mapped[int] = mapped_column(Integer)
    shipping_paise: Mapped[int] = mapped_column(Integer, default=0)
    total_paise: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    payment_status: Mapped[str] = mapped_column(String(24), default="pending")
    fulfilment_status: Mapped[str] = mapped_column(String(24), default="unfulfilled")
    provider: Mapped[str] = mapped_column(String(40), default="sandbox")
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    items: Mapped[list["CommerceOrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    refunds: Mapped[list["Refund"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    fulfilments: Mapped[list["Fulfilment"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class CommerceOrderItem(Base):
    __tablename__ = "commerce_order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("commerce_orders.id", ondelete="CASCADE"), index=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("product_variants.id"), index=True)
    sku: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_paise: Mapped[int] = mapped_column(Integer)
    order: Mapped[CommerceOrder] = relationship(back_populates="items")


class Refund(Base):
    __tablename__ = "refunds"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    order_id: Mapped[str] = mapped_column(ForeignKey("commerce_orders.id", ondelete="CASCADE"), index=True)
    amount_paise: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(24), default="pending")
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    order: Mapped[CommerceOrder] = relationship(back_populates="refunds")


class Fulfilment(Base):
    __tablename__ = "fulfilments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    order_id: Mapped[str] = mapped_column(ForeignKey("commerce_orders.id", ondelete="CASCADE"), index=True)
    carrier: Mapped[str] = mapped_column(String(120), default="unassigned")
    tracking_number: Mapped[str | None] = mapped_column(String(160), nullable=True)
    tracking_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    order: Mapped[CommerceOrder] = relationship(back_populates="fulfilments")


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id: Mapped[str] = mapped_column(ForeignKey("catalog_products.id", ondelete="CASCADE"), index=True)
    order_id: Mapped[str | None] = mapped_column(ForeignKey("commerce_orders.id"), nullable=True)
    author_name: Mapped[str] = mapped_column(String(160))
    rating: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255), default="")
    body: Mapped[str] = mapped_column(Text)
    verified_purchase: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BatchTrace(Base):
    __tablename__ = "batch_traces"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id: Mapped[str] = mapped_column(ForeignKey("catalog_products.id", ondelete="CASCADE"), index=True)
    batch_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    origin: Mapped[str] = mapped_column(String(255))
    manufacturer: Mapped[str] = mapped_column(String(255))
    manufactured_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    report_asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), index=True)
    session_id: Mapped[str] = mapped_column(String(80), index=True)
    path: Mapped[str] = mapped_column(String(500))
    payload: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
