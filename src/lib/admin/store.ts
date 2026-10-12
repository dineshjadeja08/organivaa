import "server-only";
import type {AdminRecord,AdminResource,AdminStatus} from "./types";
import type {Product} from "@/lib/data";
export type CommerceOrder={id:string;number:string;customerEmail?:string;customerName?:string;total:number;status:string;paymentStatus:string;fulfilmentStatus:string;provider:string;createdAt:string;items:{sku:string;title:string;quantity:number;unitPrice:number}[];refunds:{id:string;amount:number;reason:string;status:string}[];fulfilments:{id:string;carrier:string;trackingNumber?:string;trackingUrl?:string;status:string}[]};
export type VerifiedReview={id:string;productId:string;author:string;rating:number;title:string;body:string;verifiedPurchase:boolean;status:string;createdAt:string};
export type BatchRecord={id:string;productId:string;product:string;batchCode:string;origin:string;manufacturer:string;manufacturedOn?:string;expiresOn?:string;status:string;reportUrl?:string};
export type AnalyticsSummary={events:Record<string,number>;orders:number;paidRevenue:number;refunded:number};

const apiBase=()=>process.env.FLASK_API_URL??"http://127.0.0.1:5000/api/v1";
const serviceToken=()=>process.env.FLASK_SERVICE_TOKEN??"organivaa-local-service-token";

async function flask<T>(path:string,init:RequestInit={}):Promise<T>{
 const response=await fetch(`${apiBase()}${path}`,{...init,cache:"no-store",signal:AbortSignal.timeout(5000),headers:{"content-type":"application/json","x-service-token":serviceToken(),"x-operator":"organivaa-next-admin",...init.headers}});
 const body=await response.json().catch(()=>({error:"Invalid Flask response"}));
 if(!response.ok)throw new Error(body.error??`Flask API returned ${response.status}`);
 return body as T;
}

export async function backendHealth(){try{return await flask<{status:string;database:string}>("/health")}catch{return {status:"unavailable",database:"unavailable"}}}
export async function listRecords(resource:AdminResource){const result=await flask<{data:AdminRecord[]}>(`/admin/${resource}`);return result.data}
export async function createRecord(resource:AdminResource,input:AdminRecord){const result=await flask<{data:AdminRecord}>(`/admin/${resource}`,{method:"POST",body:JSON.stringify(input)});return result.data}
export async function updateRecord(resource:AdminResource,id:string,status:AdminStatus){const result=await flask<{data:AdminRecord}>(`/admin/${resource}`,{method:"PATCH",body:JSON.stringify({id,status})});return result.data}
export async function deleteRecord(resource:AdminResource,id:string){await flask(`/admin/${resource}`,{method:"DELETE",body:JSON.stringify({id})});return {id}}
export async function getAdminSummary(){return (await flask<{data:{counts:Record<string,Record<string,number>>;audit:AdminRecord[]}}>("/admin/summary")).data}
export async function listCatalogProducts(){return (await flask<{data:Product[]}>("/admin/catalog/products")).data}
export async function listCommerceOrders(){return (await flask<{data:CommerceOrder[]}>("/admin/orders")).data}
export async function listVerifiedReviews(){return (await flask<{data:VerifiedReview[]}>("/admin/reviews")).data}
export async function listBatchRecords(){return (await flask<{data:BatchRecord[]}>("/admin/batches")).data}
export async function getAnalyticsSummary(){return (await flask<{data:AnalyticsSummary}>("/admin/analytics/summary")).data}
