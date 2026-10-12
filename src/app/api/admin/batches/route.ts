import {NextRequest,NextResponse} from "next/server";
import {proxyAdmin} from "@/lib/admin/route-proxy";
export async function POST(request:NextRequest){const result=await proxyAdmin("/admin/batches",{method:"POST",body:await request.text()});return NextResponse.json(result.body,{status:result.status})}
