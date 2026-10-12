"use client";
import Link from "next/link";
import {useStore} from "./store-provider";
import {ProductCard} from "./product-card";
export function RecentlyViewed(){const {recent,catalog}=useStore();const items=recent.map(id=>catalog.find(p=>p.id===id)).filter((p):p is NonNullable<typeof p>=>Boolean(p)).slice(0,4);if(!items.length)return null;return <section className="section recent-section"><div className="section-head"><div><span className="eyebrow">PICK UP WHERE YOU LEFT OFF</span><h2>Recently viewed</h2></div></div><div className="product-grid">{items.map(p=><ProductCard key={p.id} product={p}/>)}</div></section>}
export function WishlistGrid(){const {wishlist,catalog}=useStore();const items=wishlist.map(id=>catalog.find(p=>p.id===id)).filter((p):p is NonNullable<typeof p>=>Boolean(p));return items.length?<div className="product-grid">{items.map(p=><ProductCard key={p.id} product={p}/>)}</div>:<div className="empty-state"><span>♡</span><h2>Your wishlist is ready for a first ritual.</h2><p>Save products here to compare them or return later.</p><Link className="btn" href="/shop">Explore all products</Link></div>}
