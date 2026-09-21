"use client";
import {useState,type CSSProperties} from "react";
import {Leaf,Coins,BookOpen,ShieldCheck,Factory,Truck,ShoppingBag} from "lucide-react";
import type {EnrichedArtifacts,GraphNode} from "@/lib/hershey/enrichedArtifacts";
import {HersheyOrb as Orb} from "./HersheyOrb";
import IngredientPanels,{formatCents,type FamilyName} from "./IngredientPanels";
import CostNodePanel from "./CostNodePanel";
import ProcessStagePanel from "./ProcessStagePanel";
import CompanyContext from "./CompanyContext";
import NodeResearch from "./NodeResearch";
import NodeConnections from "./NodeConnections";
import StoryObject,{storyObjectFor} from "./StoryObject";
import "./panel-research.css";
import "./home-evidence-stories.css";

export function familyForNode(id:string):FamilyName[]{
 if(id==="NODE_COST_INGREDIENTS")return["sugar","cocoa","dairy","minor"];
 if(/SUGAR|ASR/.test(id))return["sugar"];
 if(/COCOA|BARRY/.test(id))return["cocoa"];
 if(/DAIRY|LAND_O_LAKES/.test(id))return["dairy"];
 if(/SOY|PGPR|NATURAL/.test(id))return["minor"];
 if(/PACKAGING|WRAPPING/.test(id))return["packaging"];
 if(/PROCESS|MANUFACTURING/.test(id))return["manufacturing","packaging"];
 if(/WAREHOUSE|CARRIER|MCLANE|STORAGE|FREIGHT/.test(id))return["logistics"];
 if(/RETAIL|CONSUMER/.test(id))return["retail","residual"];
 if(/RESIDUAL/.test(id))return["residual"];
 return["sugar","cocoa","dairy","minor","packaging","manufacturing","logistics"];
}
export default function SupplySubjectDetail({data,node}:{data:EnrichedArtifacts;node:GraphNode}){
 const[tab,setTab]=useState("story");
 const families=familyForNode(node.id||""),isProcess=node.type==="manufacturing_process"||node.type==="hershey_facility",isRetail=node.type==="retailer",isDelivery=["warehouse","distributor"].includes(node.type||"");
 const ingredientRecord=data.costBreakdown.records?.find(record=>record.safe_display&&families.includes(record.family as FamilyName)&&record.ingredient_story);
 const incoming=data.graph.edges.filter(edge=>edge.target===node.id),outgoing=data.graph.edges.filter(edge=>edge.source===node.id);
 const Icon=isProcess?Factory:isRetail?ShoppingBag:isDelivery?Truck:Leaf;
 const tone=isProcess?"#f0bd89":isDelivery?"#9fddf1":isRetail?"#dfb4f1":"#a4debd";
 const retailer=isRetail?data.calculationDetails.verified_retailers.find(r=>r.retailer.toLowerCase()===(node.companyName||node.label||"").toLowerCase()):undefined;
 const description=isProcess?"Follow how ingredients are received, processed and packaged. These stages explain the modeled chocolate-making journey, rather than a confirmed proprietary line for this bar.":isDelivery?"Explore how storage and transport fit into the journey from finished goods to retail. This route is a model, not a shipment-tracking record.":isRetail?"This retailer is part of the project's shelf-price research. A price observation describes a listing, not a fixed price at every store.":node.type==="consumer"?"The shopper is the end of the illustrated product journey. This study does not track individual purchases or consumer behavior.":"Explore this ingredient or company in the wider sourcing story. Product ingredients, company relationships and cost estimates provide different kinds of information.";
 return <div className="he-stories" data-selected="true" style={{"--story-tone":tone} as CSSProperties}>
 <div className="ih-detail-tabs ss-detail-tabs" role="group" aria-label="Explore this part of the supply chain">{[{id:"story",label:"The story"},{id:"connections",label:"Connections"},...(ingredientRecord?[{id:"journey",label:"Ingredient journey"}]:[]),...(isProcess?[{id:"process",label:"Process stages"}]:[]),{id:"cost",label:"Cost per bar"},{id:"sources",label:"Reports"},...(families.length===1?[{id:"company",label:"Company context"}]:[])].map(item=><button key={item.id} aria-pressed={tab===item.id} onClick={()=>setTab(item.id)}>{item.label}</button>)}</div>
 {tab==="story"&&<section className="he-answer"><div className="panel-context-lead"><div className="panel-subject-art"><StoryObject name={storyObjectFor(node.id||"")||(isDelivery?"warehouse":isProcess?"factory":"research")}/></div><div><h3>{node.label}</h3><p>{node.description||node.hoverSummary}</p></div></div>{node.id==="NODE_PRODUCT_HERSHEY_155OZ"?<p>The product is the common reference point for the ingredient research, production model and per-bar cost comparison. Its label evidence is separate from company-wide sourcing relationships.</p>:<p>{description}</p>}{retailer&&<div className="he-fact"><ShoppingBag size={24}/><div><strong>{formatCents(retailer.price_cents_per_bar)} per bar</strong><p>Recorded retailer observation</p></div></div>}<div className="ss-connection-summary"><div><span>Coming into this subject</span><strong>{incoming.length} recorded connections</strong></div><div><span>Continuing from this subject</span><strong>{outgoing.length} recorded connections</strong></div></div><p className="he-boundary"><ShieldCheck size={20}/><span>{isRetail?"Prices can change with location, date and promotions.":"The model’s connections do not establish exact supplier allocation or a verified shipment route."}</span></p></section>}
 {tab==="journey"&&ingredientRecord&&<section className="he-answer"><h3>{ingredientRecord.label}</h3><h4>Origin context in the model</h4><p>{ingredientRecord.ingredient_story?.origin}</p><h4>How the ingredient is prepared</h4><p>{ingredientRecord.ingredient_story?.processing}</p><p className="ih-fine">This is the recorded ingredient model, not proof of a particular farm or proprietary recipe.</p></section>}
 {tab==="company"&&families.length===1&&<CompanyContext family={families[0]} data={data}/>}
 {tab==="cost"&&(isProcess?<CostNodePanel data={data} bucketId="COST_MANUFACTURING_CONVERSION"/>:<><p>Explore the existing estimate associated with this part of the journey. Shared allocations are counted once in the whole-bar model.</p><IngredientPanels key={node.id} data={data} initialFamily={families[0]} families={families}/></>)}
 {tab==="sources"&&<NodeResearch data={data} nodeId={node.id}/>}
 {tab==="connections"&&node.id&&<NodeConnections data={data} nodeId={node.id}/>}
 {tab==="process"&&node.id&&<ProcessStagePanel data={data} nodeId={node.id}/>}
 </div>;
}
