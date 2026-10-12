import "server-only";
import {createHmac,timingSafeEqual} from "node:crypto";
import {cookies} from "next/headers";

const COOKIE="organivaa-admin-session";
const payload="organivaa-admin:v1";
const secret=()=>process.env.ADMIN_SESSION_SECRET??"";
const sign=()=>createHmac("sha256",secret()).update(payload).digest("hex");
export const isDevAdmin=()=>process.env.NODE_ENV==="development"&&!process.env.ADMIN_PASSWORD;
export async function isAdmin(){if(isDevAdmin())return true;const token=(await cookies()).get(COOKIE)?.value;if(!token||!secret())return false;const expected=sign();if(token.length!==expected.length)return false;return timingSafeEqual(Buffer.from(token),Buffer.from(expected))}
export async function createAdminSession(){const jar=await cookies();jar.set(COOKIE,sign(),{httpOnly:true,sameSite:"strict",secure:process.env.NODE_ENV==="production",path:"/admin",maxAge:60*60*8,priority:"high"})}
export async function clearAdminSession(){(await cookies()).delete(COOKIE)}
export function validPassword(value:string){const configured=process.env.ADMIN_PASSWORD;if(!configured)return false;const a=Buffer.from(value);const b=Buffer.from(configured);return a.length===b.length&&timingSafeEqual(a,b)}
