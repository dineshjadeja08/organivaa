"use client";
import {createContext,useCallback,useContext,useEffect,useMemo,useState} from "react";
import type {Product} from "@/lib/data";
type Line={product:Product;quantity:number;pack:string;variantId?:string;price:number};
type Store={catalog:Product[];lines:Line[];count:number;add:(p:Product,pack?:string,price?:number,quantity?:number,variantId?:string)=>void;remove:(id:string)=>void;setQty:(id:string,n:number)=>void;clearCart:()=>void;cartOpen:boolean;setCartOpen:(v:boolean)=>void;wishlist:string[];toggleWishlist:(id:string)=>void;isWishlisted:(id:string)=>boolean;recent:string[];markViewed:(id:string)=>void};
const C=createContext<Store|null>(null);
export function StoreProvider({children,catalog}:{children:React.ReactNode;catalog:Product[]}){
 const [lines,setLines]=useState<Line[]>([]);const [cartOpen,setCartOpen]=useState(false);const [wishlist,setWishlist]=useState<string[]>([]);const [recent,setRecent]=useState<string[]>([]);const [ready,setReady]=useState(false);
 useEffect(()=>{queueMicrotask(()=>{try{const cart=localStorage.getItem("organivaa-cart");const wish=localStorage.getItem("organivaa-wishlist");const viewed=localStorage.getItem("organivaa-recent");if(cart)setLines(JSON.parse(cart));if(wish)setWishlist(JSON.parse(wish));if(viewed)setRecent(JSON.parse(viewed))}catch{}finally{setReady(true)}})},[]);
 useEffect(()=>{if(ready)localStorage.setItem("organivaa-cart",JSON.stringify(lines))},[lines,ready]);useEffect(()=>{if(ready)localStorage.setItem("organivaa-wishlist",JSON.stringify(wishlist))},[wishlist,ready]);useEffect(()=>{if(ready)localStorage.setItem("organivaa-recent",JSON.stringify(recent))},[recent,ready]);
 const markViewed=useCallback((id:string)=>setRecent(x=>[id,...x.filter(v=>v!==id)].slice(0,6)),[]);
 const value=useMemo(()=>({catalog,lines,count:lines.reduce((a,l)=>a+l.quantity,0),add:(p:Product,pack=p.packs[0].label,price=p.price,quantity=1,variantId=p.packs[0]?.id)=>{setLines(x=>{const i=x.findIndex(l=>l.product.id===p.id&&l.pack===pack);return i<0?[...x,{product:p,quantity,pack,price,variantId}]:x.map((l,j)=>j===i?{...l,quantity:l.quantity+quantity}:l)});setCartOpen(true)},remove:(id:string)=>setLines(x=>x.filter(l=>l.product.id!==id)),setQty:(id:string,n:number)=>setLines(x=>x.map(l=>l.product.id===id?{...l,quantity:Math.max(1,n)}:l)),clearCart:()=>setLines([]),cartOpen,setCartOpen,wishlist,toggleWishlist:(id:string)=>setWishlist(x=>x.includes(id)?x.filter(v=>v!==id):[...x,id]),isWishlisted:(id:string)=>wishlist.includes(id),recent,markViewed}),[catalog,lines,cartOpen,wishlist,recent,markViewed]);
 return <C.Provider value={value}>{children}</C.Provider>
}
export const useStore=()=>{const v=useContext(C);if(!v)throw Error("StoreProvider missing");return v};
