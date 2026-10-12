import {NextResponse} from "next/server";
import {getCatalogProducts} from "@/lib/catalog";
export async function GET(){try{return NextResponse.json({data:await getCatalogProducts()})}catch(error){return NextResponse.json({error:error instanceof Error?error.message:"Catalog unavailable"},{status:503})}}
