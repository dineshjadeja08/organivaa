export const adminResources = ["products","orders","inventory","customers","content","claims","promotions","support","reviews","quality"] as const;
export type AdminResource = (typeof adminResources)[number];
export type AdminStatus = "active"|"draft"|"pending"|"attention"|"archived"|"fulfilled"|"approved"|"rejected";
export type AdminRecord = {id:string;title:string;subtitle:string;status:AdminStatus;value?:string;updated:string};
