import {NextResponse} from "next/server";
import {isAdmin} from "@/lib/admin/auth";
const base=()=>process.env.FLASK_API_URL??"http://127.0.0.1:5000/api/v1";const headers=()=>({"content-type":"application/json","x-service-token":process.env.FLASK_SERVICE_TOKEN??"organivaa-local-service-token","x-operator":"organivaa-next-admin"});
async function proxy(request:Request,id:string,method:string){if(!await isAdmin())return NextResponse.json({error:"Unauthorized"},{status:401});try{const r=await fetch(`${base()}/admin/catalog/products/${encodeURIComponent(id)}`,{method,headers:headers(),body:method==="PATCH"?JSON.stringify(await request.json()):undefined,cache:"no-store"});return NextResponse.json(await r.json(),{status:r.status})}catch{return NextResponse.json({error:"Flask catalog unavailable"},{status:503})}}
export async function PATCH(request:Request,{params}:{params:Promise<{id:string}>}){return proxy(request,(await params).id,"PATCH")}
export async function DELETE(request:Request,{params}:{params:Promise<{id:string}>}){return proxy(request,(await params).id,"DELETE")}
