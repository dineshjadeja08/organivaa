import {NextResponse} from "next/server";
import {z} from "zod";
import {isAdmin} from "@/lib/admin/auth";
import {adminResources,type AdminResource} from "@/lib/admin/types";
import {createRecord,deleteRecord,listRecords,updateRecord} from "@/lib/admin/store";

const status=z.enum(["active","draft","pending","attention","archived","fulfilled","approved","rejected"]);
const updateSchema=z.object({id:z.string().min(1),status});
const createSchema=z.object({id:z.string().min(1).max(80),title:z.string().min(1).max(255),subtitle:z.string().max(500).default(""),status,value:z.string().max(120).optional()});
const deleteSchema=z.object({id:z.string().min(1)});
function resourceOf(value:string):AdminResource|null{return adminResources.includes(value as AdminResource)?value as AdminResource:null}
function errorResponse(error:unknown){const message=error instanceof Error?error.message:"Backend request failed";return NextResponse.json({error:message},{status:message.includes("Not found")?404:502})}

export async function GET(_:Request,{params}:{params:Promise<{resource:string}>}){if(!await isAdmin())return NextResponse.json({error:"Unauthorized"},{status:401});const resource=resourceOf((await params).resource);if(!resource)return NextResponse.json({error:"Unknown resource"},{status:404});try{return NextResponse.json({data:await listRecords(resource),provider:"flask-sqlalchemy"})}catch(error){return errorResponse(error)}}
export async function POST(request:Request,{params}:{params:Promise<{resource:string}>}){if(!await isAdmin())return NextResponse.json({error:"Unauthorized"},{status:401});const resource=resourceOf((await params).resource);if(!resource)return NextResponse.json({error:"Unknown resource"},{status:404});const parsed=createSchema.safeParse(await request.json().catch(()=>null));if(!parsed.success)return NextResponse.json({error:"Invalid request",details:parsed.error.flatten()},{status:400});try{return NextResponse.json({data:await createRecord(resource,{...parsed.data,updated:"Just now"})},{status:201})}catch(error){return errorResponse(error)}}
export async function PATCH(request:Request,{params}:{params:Promise<{resource:string}>}){if(!await isAdmin())return NextResponse.json({error:"Unauthorized"},{status:401});const resource=resourceOf((await params).resource);if(!resource)return NextResponse.json({error:"Unknown resource"},{status:404});const parsed=updateSchema.safeParse(await request.json().catch(()=>null));if(!parsed.success)return NextResponse.json({error:"Invalid request",details:parsed.error.flatten()},{status:400});try{return NextResponse.json({data:await updateRecord(resource,parsed.data.id,parsed.data.status)})}catch(error){return errorResponse(error)}}
export async function DELETE(request:Request,{params}:{params:Promise<{resource:string}>}){if(!await isAdmin())return NextResponse.json({error:"Unauthorized"},{status:401});const resource=resourceOf((await params).resource);if(!resource)return NextResponse.json({error:"Unknown resource"},{status:404});const parsed=deleteSchema.safeParse(await request.json().catch(()=>null));if(!parsed.success)return NextResponse.json({error:"Invalid request"},{status:400});try{return NextResponse.json({data:await deleteRecord(resource,parsed.data.id)})}catch(error){return errorResponse(error)}}
