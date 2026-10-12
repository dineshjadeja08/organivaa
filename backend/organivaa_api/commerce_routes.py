import json
import mimetypes
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, request, send_from_directory
from sqlalchemy import func, select
from werkzeug.utils import secure_filename

from .auth import require_service
from .database import db_session
from .models import AnalyticsEvent, Asset, AuditEvent, BatchTrace, CatalogProduct, CommerceOrder, CommerceOrderItem, Fulfilment, ProductVariant, Refund, Review

commerce = Blueprint("commerce", __name__)
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/avif", "application/pdf"}
ALLOWED_EXTENSIONS = {"image/jpeg": {".jpg", ".jpeg"}, "image/png": {".png"}, "image/webp": {".webp"}, "image/avif": {".avif"}, "application/pdf": {".pdf"}}


def product_json(product):
    variants=[v for v in product.variants if v.status=="active"]
    first=variants[0] if variants else None
    images=[product.primary_image]+[f"/api/media/{a.filename}" for a in product.assets if a.kind=="image"]
    return {"id":product.id,"handle":product.handle,"name":product.name,"purpose":product.purpose,"description":product.description,"ingredient":product.ingredient,"format":product.format,"concern":product.concern,"origin":product.origin,"ritual":product.ritual,"badge":product.badge,"accent":product.accent,"status":product.status,"image":images[0],"images":images,"packSize":first.pack_size if first else "","servings":first.servings if first else 0,"price":(first.price_paise//100) if first else 0,"mrp":(first.mrp_paise//100) if first and first.mrp_paise else None,"soldOut":not first or all(v.stock<=0 for v in variants),"packs":[{"id":v.id,"sku":v.sku,"label":v.label,"detail":v.detail,"packSize":v.pack_size,"servings":v.servings,"price":v.price_paise//100,"mrp":v.mrp_paise//100 if v.mrp_paise else None,"stock":v.stock} for v in variants],"seo":{"title":product.seo_title,"description":product.seo_description}}


def order_json(order):
    return {"id":order.id,"number":order.number,"customerEmail":order.customer_email,"customerName":order.customer_name,"currency":order.currency,"subtotal":order.subtotal_paise//100,"shipping":order.shipping_paise//100,"total":order.total_paise//100,"status":order.status,"paymentStatus":order.payment_status,"fulfilmentStatus":order.fulfilment_status,"provider":order.provider,"createdAt":order.created_at.isoformat(),"items":[{"sku":i.sku,"title":i.title,"quantity":i.quantity,"unitPrice":i.unit_price_paise//100} for i in order.items],"refunds":[{"id":r.id,"amount":r.amount_paise//100,"reason":r.reason,"status":r.status} for r in order.refunds],"fulfilments":[{"id":f.id,"carrier":f.carrier,"trackingNumber":f.tracking_number,"trackingUrl":f.tracking_url,"status":f.status} for f in order.fulfilments]}


@commerce.get("/catalog/products")
def list_catalog():
    session=db_session()
    try:
        products=session.scalars(select(CatalogProduct).where(CatalogProduct.status=="active").order_by(CatalogProduct.created_at)).unique().all()
        return {"data":[product_json(p) for p in products]}
    finally: session.close()


@commerce.get("/catalog/products/<handle>")
def get_catalog_product(handle):
    session=db_session()
    try:
        product=session.scalar(select(CatalogProduct).where(CatalogProduct.handle==handle,CatalogProduct.status=="active"))
        return ({"data":product_json(product)} if product else ({"error":"Not found"},404))
    finally: session.close()


@commerce.route("/admin/catalog/products",methods=["GET","POST"])
@require_service
def admin_catalog():
    session=db_session()
    try:
        if request.method=="GET":
            products=session.scalars(select(CatalogProduct).order_by(CatalogProduct.updated_at.desc())).unique().all()
            return {"data":[product_json(p) for p in products]}
        body=request.get_json(silent=True) or {}
        required=("handle","name","purpose","ingredient","format","concern")
        if any(not str(body.get(x,"")).strip() for x in required): return {"error":"Missing required product fields"},400
        if session.scalar(select(CatalogProduct).where(CatalogProduct.handle==body["handle"])): return {"error":"Handle already exists"},409
        product=CatalogProduct(handle=body["handle"],name=body["name"],purpose=body["purpose"],description=body.get("description",body["purpose"]),ingredient=body["ingredient"],format=body["format"],concern=body["concern"],origin=body.get("origin","Verification pending"),ritual=body.get("ritual","Follow pack directions"),badge=body.get("badge"),accent=body.get("accent","botanical"),primary_image=body.get("image","/images/organivaa-hero-branded.png"),status=body.get("status","draft"),seo_title=body.get("seoTitle"),seo_description=body.get("seoDescription"))
        session.add(product);session.flush();session.add(AuditEvent(action="create",resource="catalog",record_id=product.id,summary=f"Created catalog product {product.name}"));session.commit()
        return {"data":product_json(product)},201
    except Exception: session.rollback();raise
    finally: session.close()


@commerce.route("/admin/catalog/products/<product_id>",methods=["GET","PATCH","DELETE"])
@require_service
def admin_catalog_product(product_id):
    session=db_session()
    try:
        product=session.get(CatalogProduct,product_id)
        if not product:return {"error":"Not found"},404
        if request.method=="GET":return {"data":product_json(product)}
        if request.method=="DELETE":
            product.status="archived";session.add(AuditEvent(action="archive",resource="catalog",record_id=product.id,summary=f"Archived {product.name}"));session.commit();return {"data":product_json(product)}
        body=request.get_json(silent=True) or {}
        fields={"name":"name","purpose":"purpose","description":"description","ingredient":"ingredient","format":"format","concern":"concern","origin":"origin","ritual":"ritual","badge":"badge","accent":"accent","image":"primary_image","status":"status","seoTitle":"seo_title","seoDescription":"seo_description"}
        for source,target in fields.items():
            if source in body:setattr(product,target,body[source])
        session.add(AuditEvent(action="update",resource="catalog",record_id=product.id,summary=f"Updated {product.name}"));session.commit();return {"data":product_json(product)}
    except Exception:session.rollback();raise
    finally:session.close()


@commerce.post("/admin/catalog/products/<product_id>/variants")
@require_service
def add_variant(product_id):
    body=request.get_json(silent=True) or {};session=db_session()
    try:
        if not session.get(CatalogProduct,product_id):return {"error":"Product not found"},404
        if any(body.get(x) in (None,"") for x in ("sku","label","packSize","servings","price")):return {"error":"SKU, label, pack size, servings and price are required"},400
        variant=ProductVariant(product_id=product_id,sku=str(body["sku"]),label=str(body["label"]),detail=str(body.get("detail","")),pack_size=str(body["packSize"]),servings=int(body["servings"]),price_paise=int(body["price"])*100,mrp_paise=int(body["mrp"])*100 if body.get("mrp") else None,stock=int(body.get("stock",0)),position=int(body.get("position",0)),status=str(body.get("status","active")))
        session.add(variant);session.add(AuditEvent(action="create",resource="variant",record_id=variant.sku,summary=f"Created variant {variant.sku}"));session.commit();return {"data":{"id":variant.id,"sku":variant.sku}},201
    except Exception:session.rollback();raise
    finally:session.close()


@commerce.post("/admin/uploads")
@require_service
def upload_asset():
    file=request.files.get("file")
    if not file or not file.filename:return {"error":"A file is required"},400
    mime=file.mimetype or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    if mime not in ALLOWED_MIME:return {"error":"Only JPG, PNG, WebP, AVIF and PDF files are allowed"},415
    original=secure_filename(file.filename);extension=Path(original).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS[mime]:return {"error":"File extension does not match its content type"},415
    filename=f"{uuid4().hex}{extension}"
    upload_dir=Path(current_app.root_path).parents[0]/"uploads";upload_dir.mkdir(parents=True,exist_ok=True);path=upload_dir/filename;file.save(path)
    session=db_session()
    try:
        product_id=request.form.get("productId") or None
        if product_id and not session.get(CatalogProduct,product_id):path.unlink(missing_ok=True);return {"error":"Product not found"},404
        asset=Asset(product_id=product_id,original_name=original,filename=filename,mime_type=mime,size_bytes=path.stat().st_size,kind="document" if mime=="application/pdf" else "image",alt_text=request.form.get("alt","")[:255],position=int(request.form.get("position","0")))
        session.add(asset);session.flush();session.add(AuditEvent(action="upload",resource="asset",record_id=asset.id,summary=f"Uploaded {original}"));session.commit();return {"data":{"id":asset.id,"url":f"/api/media/{filename}","name":original,"mimeType":mime,"size":asset.size_bytes}},201
    except Exception:session.rollback();path.unlink(missing_ok=True);raise
    finally:session.close()


@commerce.get("/media/<filename>")
def media(filename):
    directory=Path(current_app.root_path).parents[0]/"uploads"
    return send_from_directory(directory,secure_filename(filename),max_age=31536000)


@commerce.post("/shipping/quote")
def shipping_quote():
    body=request.get_json(silent=True) or {};pincode=str(body.get("pincode",""));subtotal=int(body.get("subtotal",0))
    if len(pincode)!=6 or not pincode.isdigit():return {"error":"Enter a valid 6-digit pincode"},400
    amount=0 if subtotal>=999 else 99
    return {"data":{"serviceable":True,"shipping":amount,"currency":"INR","provider":current_app.config["SHIPPING_PROVIDER"],"estimatedDelivery":None,"message":"Live delivery dates require configured courier credentials."}}


@commerce.post("/checkout/session")
def checkout_session():
    body=request.get_json(silent=True) or {};lines=body.get("lines") or []
    if not lines:return {"error":"Cart is empty"},400
    session=db_session()
    try:
        items=[];subtotal=0
        for line in lines:
            variant=session.get(ProductVariant,str(line.get("variantId","")));quantity=max(1,min(10,int(line.get("quantity",1))))
            if not variant or variant.status!="active":return {"error":"A selected product variant is unavailable"},409
            if variant.stock<quantity:return {"error":f"Insufficient stock for {variant.sku}"},409
            subtotal+=variant.price_paise*quantity;items.append((variant,quantity))
        shipping=0 if subtotal>=99900 else 9900;number=f"ORG-{datetime.now(timezone.utc):%y%m%d}-{uuid4().hex[:6].upper()}"
        order=CommerceOrder(number=number,customer_email=body.get("email"),customer_name=body.get("name"),subtotal_paise=subtotal,shipping_paise=shipping,total_paise=subtotal+shipping,provider=current_app.config["PAYMENT_PROVIDER"],address_json=json.dumps(body.get("address") or {}))
        session.add(order);session.flush()
        for variant,quantity in items:session.add(CommerceOrderItem(order_id=order.id,variant_id=variant.id,sku=variant.sku,title=variant.product.name,quantity=quantity,unit_price_paise=variant.price_paise))
        session.add(AuditEvent(action="create",resource="order",record_id=number,summary=f"Created checkout {number}"));session.commit()
        return {"data":{"order":order_json(order),"checkoutUrl":f"/checkout/sandbox/{number}","provider":order.provider,"live":order.provider!="sandbox"}},201
    except Exception:session.rollback();raise
    finally:session.close()


@commerce.get("/orders/<number>")
def track_order(number):
    email=request.args.get("email","").lower();session=db_session()
    try:
        order=session.scalar(select(CommerceOrder).where(CommerceOrder.number==number))
        if not order or not order.customer_email or order.customer_email.lower()!=email:return {"error":"Order not found"},404
        return {"data":order_json(order)}
    finally:session.close()


@commerce.get("/admin/orders")
@require_service
def admin_orders():
    session=db_session()
    try:return {"data":[order_json(o) for o in session.scalars(select(CommerceOrder).order_by(CommerceOrder.created_at.desc())).unique().all()]}
    finally:session.close()


@commerce.post("/admin/orders/<order_id>/refunds")
@require_service
def create_refund(order_id):
    body=request.get_json(silent=True) or {};session=db_session()
    try:
        order=session.get(CommerceOrder,order_id)
        if not order:return {"error":"Order not found"},404
        amount=int(body.get("amount",0))*100
        already_refunded=sum(refund.amount_paise for refund in order.refunds if refund.status not in {"failed","cancelled"})
        if amount<=0 or amount+already_refunded>order.total_paise:return {"error":"Refund exceeds the remaining refundable amount"},400
        refund=Refund(order_id=order.id,amount_paise=amount,reason=str(body.get("reason","Operator refund")),status="pending" if order.provider=="sandbox" else "requested")
        session.add(refund);session.add(AuditEvent(action="refund",resource="order",record_id=order.number,summary=f"Refund requested for ₹{amount//100}"));session.commit();return {"data":order_json(order)},201
    except Exception:session.rollback();raise
    finally:session.close()


@commerce.post("/admin/orders/<order_id>/fulfilments")
@require_service
def create_fulfilment(order_id):
    body=request.get_json(silent=True) or {};session=db_session()
    try:
        order=session.get(CommerceOrder,order_id)
        if not order:return {"error":"Order not found"},404
        fulfilment=Fulfilment(order_id=order.id,carrier=str(body.get("carrier","unassigned")),tracking_number=body.get("trackingNumber"),tracking_url=body.get("trackingUrl"),status=str(body.get("status","pending")));order.fulfilment_status=fulfilment.status
        session.add(fulfilment);session.add(AuditEvent(action="fulfil",resource="order",record_id=order.number,summary=f"Fulfilment updated to {fulfilment.status}"));session.commit();return {"data":order_json(order)},201
    except Exception:session.rollback();raise
    finally:session.close()


@commerce.post("/reviews")
def submit_review():
    body=request.get_json(silent=True) or {};session=db_session()
    try:
        product=session.scalar(select(CatalogProduct).where(CatalogProduct.handle==body.get("handle")))
        if not product or not 1<=int(body.get("rating",0))<=5 or len(str(body.get("body","")))<10:return {"error":"Valid product, rating and review text are required"},400
        order=session.scalar(select(CommerceOrder).where(CommerceOrder.number==body.get("orderNumber"),func.lower(CommerceOrder.customer_email)==str(body.get("email","")).lower())) if body.get("orderNumber") else None
        if order and not session.scalar(select(CommerceOrderItem.id).join(ProductVariant,CommerceOrderItem.variant_id==ProductVariant.id).where(CommerceOrderItem.order_id==order.id,ProductVariant.product_id==product.id)):order=None
        review=Review(product_id=product.id,order_id=order.id if order else None,author_name=str(body.get("author","Customer"))[:160],rating=int(body["rating"]),title=str(body.get("title",""))[:255],body=str(body["body"]),verified_purchase=bool(order),status="pending")
        session.add(review);session.commit();return {"data":{"id":review.id,"status":"pending","verifiedPurchase":review.verified_purchase}},201
    except Exception:session.rollback();raise
    finally:session.close()


@commerce.get("/products/<handle>/reviews")
def approved_reviews(handle):
    session=db_session()
    try:
        product=session.scalar(select(CatalogProduct).where(CatalogProduct.handle==handle));reviews=session.scalars(select(Review).where(Review.product_id==product.id,Review.status=="approved",Review.verified_purchase.is_(True)).order_by(Review.created_at.desc())).all() if product else []
        return {"data":[{"id":r.id,"author":r.author_name,"rating":r.rating,"title":r.title,"body":r.body,"verifiedPurchase":True,"createdAt":r.created_at.isoformat()} for r in reviews]}
    finally:session.close()


def review_json(review):
    return {"id":review.id,"productId":review.product_id,"author":review.author_name,"rating":review.rating,"title":review.title,"body":review.body,"verifiedPurchase":review.verified_purchase,"status":review.status,"createdAt":review.created_at.isoformat()}


@commerce.get("/admin/reviews")
@require_service
def admin_reviews():
    session=db_session()
    try:return {"data":[review_json(review) for review in session.scalars(select(Review).order_by(Review.created_at.desc())).all()]}
    finally:session.close()


@commerce.patch("/admin/reviews/<review_id>")
@require_service
def moderate_review(review_id):
    body=request.get_json(silent=True) or {};status=str(body.get("status",""))
    if status not in {"pending","approved","rejected"}:return {"error":"Status must be pending, approved or rejected"},400
    session=db_session()
    try:
        review=session.get(Review,review_id)
        if not review:return {"error":"Review not found"},404
        if status=="approved" and not review.verified_purchase:return {"error":"Only verified-purchase reviews can be approved"},409
        review.status=status;session.add(AuditEvent(action="moderate",resource="review",record_id=review.id,summary=f"Review marked {status}"));session.commit();return {"data":review_json(review)}
    except Exception:session.rollback();raise
    finally:session.close()


def batch_json(batch,session):
    product=session.get(CatalogProduct,batch.product_id)
    asset=session.get(Asset,batch.report_asset_id) if batch.report_asset_id else None
    return {"id":batch.id,"productId":batch.product_id,"product":product.name if product else "Unknown product","batchCode":batch.batch_code,"origin":batch.origin,"manufacturer":batch.manufacturer,"manufacturedOn":str(batch.manufactured_on) if batch.manufactured_on else None,"expiresOn":str(batch.expires_on) if batch.expires_on else None,"status":batch.status,"reportUrl":f"/api/media/{asset.filename}" if asset else None}


@commerce.route("/admin/batches",methods=["GET","POST"])
@require_service
def admin_batches():
    session=db_session()
    try:
        if request.method=="GET":return {"data":[batch_json(batch,session) for batch in session.scalars(select(BatchTrace).order_by(BatchTrace.created_at.desc())).all()]}
        body=request.get_json(silent=True) or {}
        if any(not body.get(field) for field in ("productId","batchCode","origin","manufacturer")):return {"error":"Product, batch code, origin and manufacturer are required"},400
        if not session.get(CatalogProduct,str(body["productId"])):return {"error":"Product not found"},404
        batch=BatchTrace(product_id=str(body["productId"]),batch_code=str(body["batchCode"]).strip(),origin=str(body["origin"]),manufacturer=str(body["manufacturer"]),manufactured_on=date.fromisoformat(body["manufacturedOn"]) if body.get("manufacturedOn") else None,expires_on=date.fromisoformat(body["expiresOn"]) if body.get("expiresOn") else None,status="draft",report_asset_id=body.get("reportAssetId") or None)
        session.add(batch);session.flush();session.add(AuditEvent(action="create",resource="batch",record_id=batch.id,summary=f"Created batch {batch.batch_code}"));session.commit();return {"data":batch_json(batch,session)},201
    except ValueError:return {"error":"Dates must use YYYY-MM-DD"},400
    except Exception:session.rollback();raise
    finally:session.close()


@commerce.patch("/admin/batches/<batch_id>")
@require_service
def update_batch(batch_id):
    body=request.get_json(silent=True) or {};session=db_session()
    try:
        batch=session.get(BatchTrace,batch_id)
        if not batch:return {"error":"Batch not found"},404
        status=str(body.get("status",batch.status))
        if status not in {"draft","approved","rejected"}:return {"error":"Invalid batch status"},400
        if status=="approved" and not (body.get("reportAssetId") or batch.report_asset_id):return {"error":"An approved evidence document is required before publication"},409
        for source,target in (("origin","origin"),("manufacturer","manufacturer"),("reportAssetId","report_asset_id")):
            if source in body:setattr(batch,target,body[source] or None)
        batch.status=status;session.add(AuditEvent(action="update",resource="batch",record_id=batch.id,summary=f"Batch {batch.batch_code} marked {status}"));session.commit();return {"data":batch_json(batch,session)}
    except Exception:session.rollback();raise
    finally:session.close()


@commerce.get("/trace/<batch_code>")
def trace_batch(batch_code):
    session=db_session()
    try:
        batch=session.scalar(select(BatchTrace).where(BatchTrace.batch_code==batch_code,BatchTrace.status=="approved"))
        if not batch:return {"error":"No approved batch record found"},404
        product=session.get(CatalogProduct,batch.product_id);return {"data":{"batchCode":batch.batch_code,"product":product.name,"origin":batch.origin,"manufacturer":batch.manufacturer,"manufacturedOn":str(batch.manufactured_on) if batch.manufactured_on else None,"expiresOn":str(batch.expires_on) if batch.expires_on else None,"reportUrl":f"/api/media/{session.get(Asset,batch.report_asset_id).filename}" if batch.report_asset_id else None}}
    finally:session.close()


@commerce.post("/analytics/events")
def analytics_event():
    body=request.get_json(silent=True) or {};allowed={"page_view","view_product","add_to_cart","begin_checkout","purchase","search","wishlist"}
    if body.get("name") not in allowed:return {"error":"Unsupported event"},400
    session=db_session()
    try:
        event=AnalyticsEvent(name=body["name"],session_id=str(body.get("sessionId","anonymous"))[:80],path=str(body.get("path","/"))[:500],payload=json.dumps(body.get("payload") or {}));session.add(event);session.commit();return {"accepted":True},202
    finally:session.close()


@commerce.get("/admin/analytics/summary")
@require_service
def analytics_summary():
    session=db_session()
    try:
        event_counts=dict(session.execute(select(AnalyticsEvent.name,func.count(AnalyticsEvent.id)).group_by(AnalyticsEvent.name)).all())
        order_count=session.scalar(select(func.count()).select_from(CommerceOrder)) or 0
        revenue=session.scalar(select(func.coalesce(func.sum(CommerceOrder.total_paise),0)).where(CommerceOrder.payment_status=="paid")) or 0
        refunded=session.scalar(select(func.coalesce(func.sum(Refund.amount_paise),0)).where(Refund.status.in_(("succeeded","completed")))) or 0
        return {"data":{"events":event_counts,"orders":order_count,"paidRevenue":int(revenue)//100,"refunded":int(refunded)//100}}
    finally:session.close()
