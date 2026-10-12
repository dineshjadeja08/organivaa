"use client";
import {Bell,Check,Heart,Truck} from "lucide-react";
import {useEffect,useState} from "react";
import type {Product} from "@/lib/data";
import {money} from "@/lib/data";
import {useStore} from "./store-provider";

export function ProductBuy({product}:{product:Product}){
 const [pack,setPack]=useState(product.packs[0]);const [pin,setPin]=useState("");const [message,setMessage]=useState("");const [qty,setQty]=useState(1);const [stockEmail,setStockEmail]=useState("");const [stockMessage,setStockMessage]=useState("");
 const {add,toggleWishlist,isWishlisted,markViewed}=useStore();
 useEffect(()=>markViewed(product.id),[markViewed,product.id]);
 const wished=isWishlisted(product.id);const perServing=Math.round(pack.price/(pack.servings||product.servings||1));
 async function check(){if(!/^\d{6}$/.test(pin)){setMessage("Enter a valid 6-digit Indian pincode.");return}setMessage("Checking serviceability…");try{const response=await fetch("/api/shipping/quote",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({pincode:pin,subtotal:pack.price*qty})});const body=await response.json();setMessage(response.ok?`${body.data.serviceable?"Delivery is available.":"Delivery is unavailable."} ${body.data.shipping===0?"Free shipping applies.":`Shipping is ${money(body.data.shipping)}.`} ${body.data.message}`:body.error)}catch{setMessage("Delivery service is temporarily unavailable.")}}
 function addToBag(){add(product,pack.label,pack.price,qty,pack.id);void fetch("/api/analytics",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({name:"add_to_cart",sessionId:"browser",path:location.pathname,payload:{productId:product.id,variantId:pack.id,quantity:qty}})})}
 function requestStock(e:React.FormEvent){e.preventDefault();setStockMessage(/^\S+@\S+\.\S+$/.test(stockEmail)?"Alert request saved in this demo. Connect an email provider before launch to send notifications.":"Enter a valid email address.")}
 return <>
  <div className="pdp-price"><b>{money(pack.price)}</b>{product.mrp&&pack.id==="1"&&<s>{money(product.mrp)}</s>}<small>{money(perServing)} per serving</small></div>
  <fieldset className="pack-field"><legend>Choose your pack</legend><div className="pack-options">{product.packs.map(x=><label className={`pack-option ${pack.id===x.id?"selected":""}`} key={x.id}><span><input type="radio" name="pack" checked={pack.id===x.id} onChange={()=>setPack(x)}/> {x.label}<small>{x.detail}</small></span><b>{money(x.price)}</b></label>)}</div></fieldset>
  <div className="purchase-mode"><span><Check/> One-time purchase</span><span aria-disabled="true">Subscribe & save <small>Coming after provider approval</small></span></div>
  <label htmlFor="pin">Check delivery</label><div className="pincode"><input id="pin" inputMode="numeric" maxLength={6} value={pin} onChange={e=>setPin(e.target.value.replace(/\D/g,""))} placeholder="Enter 6-digit pincode"/><button onClick={check}>Check</button></div>{message&&<p className="pdp-note" role="status">{message}</p>}
  {product.soldOut?<form className="stock-alert" onSubmit={requestStock}><Bell/><div><b>Back-in-stock alert</b><p>Leave your email to prepare an alert request.</p></div><input aria-label="Email for stock alert" type="email" value={stockEmail} onChange={e=>setStockEmail(e.target.value)} placeholder="Email address"/><button className="btn">Notify me</button>{stockMessage&&<small role="status">{stockMessage}</small>}</form>:<div className="buy-row"><select aria-label="Quantity" value={qty} onChange={e=>setQty(Number(e.target.value))}><option>1</option><option>2</option><option>3</option></select><button className="btn" onClick={addToBag}>Add to bag</button></div>}
  <button className={`save-pdp ${wished?"active":""}`} onClick={()=>toggleWishlist(product.id)}><Heart fill={wished?"currentColor":"none"}/> {wished?"Saved to wishlist":"Save for later"}</button>
  <div className="buy-assurances"><span><Truck/> Free shipping over ₹999</span><span><Check/> Secure hosted checkout</span></div>
  <p className="pdp-note">Taxes included. Payment methods, COD eligibility and final delivery date are shown at checkout. Returns are subject to the published policy.</p>
  {!product.soldOut&&<div className="mobile-buy"><span><b>{money(pack.price)}</b><small>{pack.label}</small></span><button onClick={addToBag}>Add to bag</button></div>}
 </>
}
