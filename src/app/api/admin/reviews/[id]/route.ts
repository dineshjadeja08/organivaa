import {NextRequest,NextResponse} from "next/server";
import {proxyAdmin} from "@/lib/admin/route-proxy";
export async function PATCH(request:NextRequest,{params}:{params:Promise<{id:string}>}){const {id}=await params;const result=await proxyAdmin(`/admin/reviews/${encodeURIComponent(id)}`,{method:"PATCH",body:await request.text()});return NextResponse.json(result.body,{status:result.status})}
