import "server-only";
import {isAdmin} from "./auth";
const base=()=>process.env.FLASK_API_URL??"http://127.0.0.1:5000/api/v1";
export async function proxyAdmin(path:string,init:RequestInit={}){
 if(!await isAdmin())return {body:{error:"Unauthorized"},status:401};
 try{const response=await fetch(`${base()}${path}`,{...init,cache:"no-store",headers:{"content-type":"application/json","x-service-token":process.env.FLASK_SERVICE_TOKEN??"organivaa-local-service-token","x-operator":"organivaa-next-admin",...init.headers}});return {body:await response.json(),status:response.status}}
 catch{return {body:{error:"Flask backend unavailable"},status:503}}
}
