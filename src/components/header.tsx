"use client";
import Image from "next/image";
import Link from "next/link";
import {ChevronDown,Heart,Menu,Search,ShoppingBag,User,X} from "lucide-react";
import {useEffect,useRef,useState} from "react";
import {articles,concerns,ingredients} from "@/lib/data";
import {useStore} from "./store-provider";

const slug=(x:string)=>x.toLowerCase().replaceAll(" & ","-").replaceAll(" ","-").replaceAll("'","");
export function Header(){
 const [mobile,setMobile]=useState(false);const [search,setSearch]=useState(false);const [q,setQ]=useState("");const input=useRef<HTMLInputElement>(null);const {catalog:products,count,setCartOpen,wishlist}=useStore();
 useEffect(()=>{if(search)input.current?.focus()},[search]);
 const query=q.trim().toLowerCase();
 const foundProducts=query?products.filter(p=>`${p.name} ${p.ingredient} ${p.concern} ${p.format}`.toLowerCase().includes(query)).slice(0,4):[];
 const foundIngredients=query?ingredients.filter(x=>x.toLowerCase().includes(query)).slice(0,4):[];
 const foundConcerns=query?concerns.filter(x=>x.toLowerCase().includes(query)).slice(0,4):[];
 const foundArticles=query?articles.filter(x=>`${x.title} ${x.category} ${x.summary}`.toLowerCase().includes(query)).slice(0,3):[];
 const closeSearch=()=>{setSearch(false);setQ("")};
 return <>
  <a className="skip" href="#main">Skip to content</a><div className="announce">Complimentary shipping on orders above ₹999 <span>· India-wide delivery, subject to serviceability</span></div>
  <header className="header"><button className="icon mobile-only" aria-label="Open menu" onClick={()=>setMobile(true)}><Menu/></button><Link href="/" className="logo">ORGANIVAA</Link>
   <nav className="desktop-nav" aria-label="Main navigation">
    <details className="nav-dropdown"><summary>Shop <ChevronDown/></summary><div className="mega-menu"><div><small>SHOP BY CONCERN</small>{concerns.slice(0,6).map(x=><Link key={x} href={`/concerns/${slug(x)}`}>{x}</Link>)}</div><div><small>SHOP BY INGREDIENT</small>{ingredients.map(x=><Link key={x} href={`/ingredients/${x.toLowerCase()}`}>{x}</Link>)}</div><div><small>SHOP BY FORMAT</small>{["Powders","Capsules","Tonics","Foods","Bundles"].map(x=><Link key={x} href={`/shop?format=${x.toLowerCase()}`}>{x}</Link>)}</div><Link className="mega-feature" href="/products/moringa-daily-greens"><Image src="/images/organivaa-moringa-branded.png" alt="Organivaa Moringa Daily Greens" fill sizes="260px"/><span><small>EDITOR&apos;S PICK</small><b>Moringa Daily Greens</b><em>Explore the morning ritual</em></span></Link></div></details>
    <Link href="/bestsellers">Bestsellers</Link><Link href="/bundles">Bundles</Link><Link href="/learn">Learn</Link><Link href="/about">Our standard</Link>
   </nav>
   <div className="utilities"><button className="icon" aria-label="Search" onClick={()=>setSearch(true)}><Search/></button><Link className="icon account-icon wish-link" href="/wishlist" aria-label={`Wishlist with ${wishlist.length} items`}><Heart/><b>{wishlist.length||""}</b></Link><Link className="icon account-icon" href="/account" aria-label="Account"><User/></Link><button className="icon cart-button" aria-label={`Cart with ${count} items`} onClick={()=>setCartOpen(true)}><ShoppingBag/><b>{count}</b></button></div>
  </header>
  {mobile&&<div className="overlay" role="dialog" aria-modal="true" aria-label="Mobile navigation"><div className="mobile-sheet"><button className="icon close" onClick={()=>setMobile(false)} aria-label="Close menu"><X/></button><span className="eyebrow">EXPLORE ORGANIVAA</span>{[["Shop all","/shop"],["Shop by concern","/concerns/daily-wellness"],["Ingredients","/ingredients"],["Bestsellers","/bestsellers"],["Bundles","/bundles"],["Wishlist","/wishlist"],["Track an order","/track-order"],["Learn","/learn"],["Our standard","/about"]].map(([a,b])=><Link key={a} href={b} onClick={()=>setMobile(false)}>{a}</Link>)}</div></div>}
  {search&&<div className="overlay search-overlay" role="dialog" aria-modal="true" aria-label="Search"><div className="search-panel"><button className="icon close" onClick={closeSearch} aria-label="Close search"><X/></button><label htmlFor="search">What can we help you find?</label><div className="search-field"><Search/><input ref={input} id="search" value={q} onChange={e=>setQ(e.target.value)} placeholder="Products, ingredients, concerns…"/></div>{!query?<div><p className="muted">POPULAR SEARCHES</p><div className="chips">{[...ingredients.slice(0,3),...concerns.slice(0,2)].map(x=><button key={x} onClick={()=>setQ(x)}>{x}</button>)}</div></div>:<div className="search-groups">{foundProducts.length>0&&<section><p className="muted">PRODUCTS</p>{foundProducts.map(p=><Link href={`/products/${p.handle}`} key={p.id} onClick={closeSearch}><span>{p.name}<small>{p.ingredient} · {p.format}</small></span><b>View</b></Link>)}</section>}{foundIngredients.length>0&&<section><p className="muted">INGREDIENTS</p>{foundIngredients.map(x=><Link key={x} href={`/ingredients/${x.toLowerCase()}`} onClick={closeSearch}>{x}</Link>)}</section>}{foundConcerns.length>0&&<section><p className="muted">CONCERNS</p>{foundConcerns.map(x=><Link key={x} href={`/concerns/${slug(x)}`} onClick={closeSearch}>{x}</Link>)}</section>}{foundArticles.length>0&&<section><p className="muted">FIELD NOTES</p>{foundArticles.map(x=><Link key={x.slug} href={`/learn/${x.slug}`} onClick={closeSearch}>{x.title}</Link>)}</section>}{!foundProducts.length&&!foundIngredients.length&&!foundConcerns.length&&!foundArticles.length&&<div className="no-results"><b>No exact matches</b><p>Try a concern such as sleep, an ingredient such as moringa, or browse all products.</p><Link className="underlink" href="/shop" onClick={closeSearch}>View all products</Link></div>}</div>}</div></div>}
 </>
}
