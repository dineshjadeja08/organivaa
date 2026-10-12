import "server-only";
import type {Product} from "@/lib/data";

const apiBase=()=>process.env.FLASK_API_URL??"http://127.0.0.1:5000/api/v1";
async function catalog<T>(path:string):Promise<T>{const response=await fetch(`${apiBase()}${path}`,{cache:"no-store",signal:AbortSignal.timeout(5000)});const body=await response.json().catch(()=>({error:"Invalid catalog response"}));if(!response.ok)throw new Error(body.error??`Catalog returned ${response.status}`);return body as T}
export async function getCatalogProducts(){return (await catalog<{data:Product[]}>("/catalog/products")).data}
export async function getCatalogProduct(handle:string){try{return (await catalog<{data:Product}>(`/catalog/products/${encodeURIComponent(handle)}`)).data}catch{return null}}
export type PublicReview={id:string;author:string;rating:number;title:string;body:string;verifiedPurchase:true;createdAt:string};
export async function getProductReviews(handle:string){try{return (await catalog<{data:PublicReview[]}>(`/products/${encodeURIComponent(handle)}/reviews`)).data}catch{return []}}
