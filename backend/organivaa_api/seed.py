import json

from sqlalchemy import func, select
from werkzeug.security import generate_password_hash

from .database import db_session
from .models import AuditEvent, CatalogProduct, Operator, ProductVariant, Record

SEED = {
    "products": [
        ("p1", "Moringa Daily Greens", "Moringa · Powders · 150 g", "active", "₹649"),
        ("p2", "Ashwagandha Calm Drops", "Ashwagandha · Tonics · 30 ml", "active", "₹799"),
        ("p3", "Turmeric + Amla Complex", "Turmeric · Capsules · 60 capsules", "active", "₹899"),
        ("p4", "Daily Ritual Trio", "Botanical blend · Bundle", "active", "₹1,899"),
        ("p5", "Shatavari Balance", "Shatavari · Capsules", "draft", "₹749"),
        ("p6", "Pure Shilajit Resin", "Shilajit · Foods · Out of stock", "attention", "₹1,299"),
    ],
    "orders": [
        ("ORD-1048", "Ananya R.", "2 items · Bengaluru", "pending", "₹1,448"),
        ("ORD-1047", "Rahul S.", "Daily Ritual Trio · Chennai", "fulfilled", "₹1,899"),
        ("ORD-1046", "Meera K.", "Moringa Daily Greens · Mumbai", "attention", "₹649"),
    ],
    "inventory": [
        ("SKU-MOR-150", "Moringa Daily Greens", "150 g · Main warehouse", "active", "84 units"),
        ("SKU-ASH-30", "Ashwagandha Calm Drops", "30 ml · Main warehouse", "attention", "9 units"),
        ("SKU-TUR-60", "Turmeric + Amla Complex", "60 capsules · Main warehouse", "active", "126 units"),
    ],
    "customers": [
        ("CUS-804", "Ananya Rao", "4 orders · Bengaluru", "active", "₹4,296 LTV"),
        ("CUS-803", "Rahul Sharma", "2 orders · Chennai", "active", "₹2,548 LTV"),
    ],
    "content": [
        ("CNT-01", "How to build a botanical ritual", "Article · Routines", "active", None),
        ("CNT-02", "Reading a wellness label", "Article · Product guides", "draft", None),
    ],
    "claims": [
        ("CLM-119", "Supports a considered evening ritual", "Ashwagandha Calm Drops · Lifestyle claim", "pending", None),
        ("CLM-118", "Made with pure moringa leaf powder", "Moringa Daily Greens · Composition claim", "approved", None),
    ],
    "promotions": [("PROMO-WELCOME", "WELCOME10", "10% first order · Min ₹999", "active", "42 uses")],
    "support": [("TKT-221", "Delivery update requested", "ORD-1046 · Meera K.", "attention", None)],
    "reviews": [("REV-QUEUE", "Verified review import", "Provider not connected", "pending", "0 verified")],
    "quality": [("DOC-MOR", "Moringa quality dossier", "Specification · batch report · certification", "draft", "0 approved")],
}


def seed_database(config, force=False):
    session = db_session()
    try:
        count = session.scalar(select(func.count()).select_from(Record)) or 0
        if force:
            session.query(Record).delete()
            session.query(AuditEvent).delete()
            count = 0
        if not count:
            for resource, entries in SEED.items():
                for external_id, title, subtitle, status, value in entries:
                    session.add(Record(resource=resource, external_id=external_id, title=title, subtitle=subtitle, status=status, value=value, payload=json.dumps({})))
        if not session.scalar(select(Operator).where(Operator.email == config["ADMIN_EMAIL"])):
            session.add(Operator(email=config["ADMIN_EMAIL"], password_hash=generate_password_hash(config["ADMIN_PASSWORD"]), role="owner"))
        session.add(AuditEvent(action="seed", resource="system", record_id="database", summary="Initial operations data created"))
        if not session.scalar(select(CatalogProduct.id).limit(1)):
            catalog = [
                ("p1","moringa-daily-greens","Moringa Daily Greens","A simple daily ritual with pure moringa leaf powder.","Moringa","Powders","Daily Wellness","India · supplier verification pending","Morning","Bestseller","moringa","/images/organivaa-moringa-branded.png",[("SKU-MOR-150","Single pack","30 servings","150 g",30,64900,74900,84),("SKU-MOR-300","2 packs","60 servings · Save ₹199","300 g",60,109900,None,40),("SKU-MOR-450","3 packs","90 servings · Save ₹398","450 g",90,154900,None,20)]),
                ("p2","ashwagandha-calm-drops","Ashwagandha Calm Drops","A considered evening botanical ritual.","Ashwagandha","Tonics","Stress & Sleep","India · supplier verification pending","Evening","New","ashwagandha","/images/organivaa-ashwagandha-branded.png",[("SKU-ASH-30","Single bottle","30 servings","30 ml",30,79900,None,9),("SKU-ASH-60","2 bottles","60 servings · Save ₹249","60 ml",60,134900,None,12)]),
                ("p3","turmeric-amla-complex","Turmeric + Amla Complex","Everyday antioxidant-rich botanical support.","Turmeric","Capsules","Immunity","India · supplier verification pending","With lunch",None,"turmeric","/images/organivaa-moringa-branded.png",[("SKU-TUR-60","1 month","60 capsules","60 capsules",30,89900,99900,126),("SKU-TUR-120","2 months","120 capsules · Save ₹299","120 capsules",60,149900,None,42)]),
                ("p4","daily-ritual-trio","Daily Ritual Trio","Three complementary rituals for morning, day and evening.","Botanical Blend","Bundles","Daily Wellness","India · documentation pending","Morning to evening","Bundle","blend","/images/organivaa-hero-branded.png",[("SKU-RITUAL-TRIO","Complete set","30-day ritual","3 products",30,189900,219900,30)]),
                ("p5","shatavari-balance","Shatavari Balance","A modern format for a time-honoured botanical.","Shatavari","Capsules","Women's Wellness","India · supplier verification pending","With a meal",None,"shatavari","/images/organivaa-ashwagandha-branded.png",[("SKU-SHA-60","1 month","60 capsules","60 capsules",30,74900,None,24)]),
                ("p6","shilajit-resin","Pure Shilajit Resin","Responsibly sourced mineral-rich resin.","Shilajit","Foods","Energy & Stamina","Source documentation pending","Morning",None,"shilajit","/images/organivaa-moringa-branded.png",[("SKU-SHI-20","20 g jar","40 servings","20 g",40,129900,None,0)]),
            ]
            for product_id,handle,name,purpose,ingredient,fmt,concern,origin,ritual,badge,accent,image,variants in catalog:
                product=CatalogProduct(id=product_id,handle=handle,name=name,purpose=purpose,description=purpose,ingredient=ingredient,format=fmt,concern=concern,origin=origin,ritual=ritual,badge=badge,accent=accent,primary_image=image,status="active")
                session.add(product)
                for position,(sku,label,detail,pack_size,servings,price,mrp,stock) in enumerate(variants):
                    session.add(ProductVariant(product_id=product_id,sku=sku,label=label,detail=detail,pack_size=pack_size,servings=servings,price_paise=price,mrp_paise=mrp,stock=stock,position=position,status="active"))
        session.commit()
        return sum(len(items) for items in SEED.values())
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
