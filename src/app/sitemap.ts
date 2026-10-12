import type {MetadataRoute} from "next";
import {getCatalogProducts} from "@/lib/catalog";
import {articles,ingredients} from "@/lib/data";
export default async function sitemap():Promise<MetadataRoute.Sitemap>{const base=process.env.NEXT_PUBLIC_SITE_URL||"http://localhost:3000";const products=await getCatalogProducts();return ["","/shop","/bestsellers","/bundles","/ingredients","/learn","/about","/contact"].map(url=>({url:base+url,lastModified:new Date()})).concat(products.map(p=>({url:`${base}/products/${p.handle}`,lastModified:new Date()})),ingredients.map(x=>({url:`${base}/ingredients/${x.toLowerCase()}`,lastModified:new Date()})),articles.map(a=>({url:`${base}/learn/${a.slug}`,lastModified:new Date()})))}
