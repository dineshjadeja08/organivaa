import Link from "next/link";
import {redirect} from "next/navigation";
import {ArrowDownRight,ArrowUpRight,Box,Clock3,Database,IndianRupee,ShoppingBag,Users} from "lucide-react";
import {AdminShell} from "@/components/admin/admin-shell";
import {isAdmin} from "@/lib/admin/auth";
import {backendHealth,getAdminSummary,listCommerceOrders,listRecords,type CommerceOrder} from "@/lib/admin/store";
import type {AdminRecord} from "@/lib/admin/types";
import {money} from "@/lib/data";

export default async function Page(){
 if(!await isAdmin())redirect("/admin/login");
 let orders:CommerceOrder[]=[];let inventory:AdminRecord[]=[];let audit:AdminRecord[]=[];let health={status:"unavailable",database:"unavailable"};
 try{[orders,inventory,health]=await Promise.all([listCommerceOrders(),listRecords("inventory"),backendHealth()]);audit=(await getAdminSummary()).audit}catch{}
 const lowStock=inventory.filter(x=>x.status==="attention").length;
 const paidRevenue=orders.filter(order=>order.paymentStatus==="paid").reduce((sum,order)=>sum+order.total,0);
 return <AdminShell title="Operations overview" description="Live controls backed by the Organivaa Flask service and relational database.">
  <section className="admin-stats"><article><span><IndianRupee/></span><div><small>PAID REVENUE</small><b>{money(paidRevenue)}</b><em className="up"><ArrowUpRight/> Captured orders only</em></div></article><article><span><ShoppingBag/></span><div><small>ORDERS IN DATABASE</small><b>{orders.length}</b><em className="up"><ArrowUpRight/> Flask live</em></div></article><article><span><Users/></span><div><small>CUSTOMER DATA</small><b>Protected</b><em className="up"><ArrowUpRight/> Minimal exposure</em></div></article><article><span><Box/></span><div><small>LOW STOCK ITEMS</small><b>{lowStock}</b><em className="down"><ArrowDownRight/> Review</em></div></article></section>
  <div className="admin-dashboard-grid"><section className="admin-panel"><div className="admin-panel-head"><div><span className="admin-kicker">LIVE OPERATIONS</span><h2>Orders needing attention</h2></div><Link href="/admin/orders">View all</Link></div><div className="admin-order-list">{orders.length?orders.slice(0,5).map(o=><Link href="/admin/orders" key={o.id}><div><b>{o.number}</b><span>{o.customerName||o.customerEmail||"Guest"} · {o.fulfilmentStatus}</span></div><div><strong>{money(o.total)}</strong><span className={`status status-${o.status}`}>{o.status}</span></div></Link>):<p className="admin-footnote">Checkout orders will appear here as they are created.</p>}</div></section><section className="admin-panel"><div className="admin-panel-head"><div><span className="admin-kicker">DATABASE AUDIT</span><h2>Recent activity</h2></div><Clock3/></div><div className="admin-activity">{audit.slice(0,5).map(a=><div key={a.id}><span></span><p><b>{a.title}</b><small>{a.subtitle} · {a.updated}</small></p></div>)}</div></section></div>
  <section className="admin-panel admin-health"><div className="admin-panel-head"><div><span className="admin-kicker">SYSTEM HEALTH</span><h2>Integration readiness</h2></div></div><div><article><b>Flask API</b><span className={`status status-${health.status==="ok"?"active":"attention"}`}>{health.status}</span><p>Authenticated server-to-server operations API.</p></article><article><b>Database</b><span className={`status status-${health.database==="connected"?"active":"attention"}`}>{health.database}</span><p>SQLite locally; PostgreSQL through DATABASE_URL.</p></article><article><b>Payment & courier</b><span className="status status-pending">sandbox</span><p>Safe end-to-end checkout is active; live credentials remain deployment-gated.</p></article><article><b>Audit log</b><span className="status status-active"><Database/> durable</span><p>Creates, updates and deletes are recorded.</p></article></div></section>
 </AdminShell>
}
