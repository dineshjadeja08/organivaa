"use client";
import Image from "next/image";
import Link from "next/link";
import {Heart,Plus} from "lucide-react";
import {useState} from "react";
import type {Product} from "@/lib/data";
import {money} from "@/lib/data";
import {useStore} from "./store-provider";

export function ProductCard({product}:{product:Product}){
 const {add,toggleWishlist,isWishlisted}=useStore();
 const [packId,setPackId]=useState(product.packs[0].id);
 const pack=product.packs.find(x=>x.id===packId)??product.packs[0];
 const wished=isWishlisted(product.id);
 return <article className="product-card">
  <div className="product-image">
   <Link href={`/products/${product.handle}`} aria-label={`View ${product.name}`}><Image src={product.image} alt={`${product.name} botanical wellness product`} fill sizes="(max-width: 768px) 50vw, 25vw"/></Link>
   {product.badge&&<span className="badge">{product.badge}</span>}
   <button className={`wish ${wished?"active":""}`} aria-label={`${wished?"Remove":"Save"} ${product.name}`} aria-pressed={wished} onClick={()=>toggleWishlist(product.id)}><Heart fill={wished?"currentColor":"none"}/></button>
   <Link className="quick-view" href={`/products/${product.handle}`}>Quick view</Link>
  </div>
  <div className="product-copy">
   <small>{product.ingredient} · {product.format}</small>
   <h3><Link href={`/products/${product.handle}`}>{product.name}</Link></h3>
   <p>{product.purpose}</p>
   <div className="product-meta"><span>{product.packSize}</span><span>{product.servings} servings</span></div>
   {product.packs.length>1&&<select className="card-pack" aria-label={`Choose pack for ${product.name}`} value={packId} onChange={e=>setPackId(e.target.value)}>{product.packs.map(x=><option key={x.id} value={x.id}>{x.label} · {money(x.price)}</option>)}</select>}
   <div className="price"><b>{money(pack.price)}</b>{product.mrp&&pack.id==="1"&&<s>{money(product.mrp)}</s>}<small>{money(Math.round(pack.price/(product.servings*Math.max(1,Number(pack.id)||1))))}/serving</small></div>
   <button className="add" disabled={product.soldOut} onClick={()=>add(product,pack.label,pack.price,1,pack.id)}>{product.soldOut?"Out of stock":<><Plus/> Add to bag</>}</button>
  </div>
 </article>
}
