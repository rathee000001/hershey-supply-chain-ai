"use client";
import NodeResearch from "./NodeResearch";
import {useState} from "react";
import Image from "next/image";
import {BookOpen,ShieldCheck} from "lucide-react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
const companyByFamily:Record<string,{id:string;file:string;role:string}>={
 sugar:{id:"SUP_ASR_SUGAR",file:"asr_logo.svg",role:"Sugar supply context"},
 cocoa:{id:"SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE",file:"barry_callebaut_logo.svg",role:"Cocoa and chocolate supply context"},
 dairy:{id:"SUP_LAND_O_LAKES_DAIRY",file:"land_olakes_logo.png",role:"Dairy supply context"},
 logistics:{id:"SUP_MCLANE_DISTRIBUTION",file:"mclane_logo.svg",role:"Distribution context"},
};
export default function CompanyContext({data,family}:{data:EnrichedArtifacts;family:string}){
 const[expanded,setExpanded]=useState(false),asset=companyByFamily[family];
 const supplier=asset&&data.suppliers.find(s=>s.supplier_packet_id===asset.id&&s.display_allowed===true);
 if(!asset||!supplier)return null;
 const modeled=supplier.relationship_level==="modeled_route_context";
 return <section className="hm-company" data-logo-theme={family==="logistics"?"dark":"light"} aria-label={asset.role}>
 <div className="hm-company-heading">{supplier.logo_allowed&&<div className="hm-company-logo"><Image src={"/data/hershey/visual_assets/source_assets/"+asset.file} alt={supplier.safe_display_name||"Company logo"} width={130} height={60} unoptimized/></div>}<div><span>{asset.role}</span><h4>{supplier.safe_display_name}</h4></div></div>
 <p>{modeled?"Shown to explain the wider distribution network. This study has not confirmed the route taken by an individual bar.":"Included in the wider company-level sourcing story. This does not establish who supplied the ingredients in this specific bar."}</p>
 <p className="hm-company-limit"><ShieldCheck size={17}/>{supplier.sku_level_confirmed?"Product-specific relationship recorded":"No exact supplier allocation claimed"}</p>
 <button className="hc-text-link" aria-expanded={expanded} onClick={()=>setExpanded(!expanded)}><BookOpen size={17}/>{expanded?"Hide supporting research":"Why this company appears"}</button>
 {expanded&&<div className="hm-company-research"><NodeResearch data={data} nodeId={({SUP_ASR_SUGAR:"NODE_SUPPLIER_ASR",SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE:"NODE_SUPPLIER_BARRY",SUP_LAND_O_LAKES_DAIRY:"NODE_SUPPLIER_LAND_O_LAKES",SUP_MCLANE_DISTRIBUTION:"NODE_DISTRIBUTOR_MCLANE"} as Record<string,string>)[supplier.supplier_packet_id||""]}/><p>These sources provide context; the company logo is identification, not proof of an exact supplier-to-product relationship.</p></div>}
 </section>;
}
