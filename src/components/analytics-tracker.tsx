"use client";
import {useEffect} from "react";
import {usePathname} from "next/navigation";
function sessionId(){const key="organivaa_session";let value=sessionStorage.getItem(key);if(!value){value=crypto.randomUUID();sessionStorage.setItem(key,value)}return value}
export function AnalyticsTracker(){const pathname=usePathname();useEffect(()=>{const payload=JSON.stringify({name:"page_view",sessionId:sessionId(),path:pathname,payload:{}});if(navigator.sendBeacon)navigator.sendBeacon("/api/analytics",new Blob([payload],{type:"application/json"}));else void fetch("/api/analytics",{method:"POST",headers:{"content-type":"application/json"},body:payload,keepalive:true})},[pathname]);return null}
