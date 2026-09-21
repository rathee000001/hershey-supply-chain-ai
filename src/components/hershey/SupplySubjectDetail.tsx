"use client";
import StoryQuestions from "./StoryQuestions";
import IngredientJourney from "./IngredientJourney";
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
import SubjectIllustration from "./SubjectIllustration";
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
 <StoryQuestions label="Explore this part of the supply chain" value={tab} onChange={setTab} items={[
{id:"story",label:"The story",question:"What role does this subject play?",hint:"Place it in the bar’s journey",art:storyObjectFor(node.id||"")||"research"},
{id:"connections",label:"Connections",question:"What comes before and after it?",hint:"Follow the recorded relationships",art:"graph"},
...(ingredientRecord?[{id:"journey",label:"Ingredient journey",question:"How does this ingredient move toward the bar?",hint:"Explore origin and preparation",art:storyObjectFor(ingredientRecord.model_ingredient_id||ingredientRecord.cost_bucket_id)||"minor"}]:[]),
...(isProcess?[{id:"process",label:"Process stages",question:"How does this step change the product?",hint:"Explore the modeled sequence",art:"factory" as const}]:[]),
{id:"cost",label:"Cost per bar",question:"What does the model allocate here?",hint:"Inspect the contribution and calculation",art:"coins"},
{id:"sources",label:"Reports",question:"What can the original sources establish?",hint:"Read the documents without leaving",art:"report"},
...(families.length===1?[{id:"company",label:"Company context",question:"How does company research fit this story?",hint:"Separate company context from exact supply",art:"factory" as const}]:[])]}/>
 {tab==="story"&&<section className="he-answer"><div className="panel-context-lead"><div className="panel-subject-art"><StoryObject name={storyObjectFor(node.id||"")||(isDelivery?"warehouse":isProcess?"factory":"research")}/></div><div><h3>{node.label}</h3><p>{node.description||node.hoverSummary}</p></div></div>{node.id==="NODE_PRODUCT_HERSHEY_155OZ"?<p>The product is the common reference point for the ingredient research, production model and per-bar cost comparison. Its label evidence is separate from company-wide sourcing relationships.</p>:<p>{description}</p>}{retailer&&<div className="he-fact"><SubjectIllustration name="retail" size={48}/><div><strong>{formatCents(retailer.price_cents_per_bar)} per bar</strong><p>Recorded retailer observation</p></div></div>}<div className="ss-connection-summary"><div><span>Coming into this subject</span><strong>{incoming.length} recorded connections</strong></div><div><span>Continuing from this subject</span><strong>{outgoing.length} recorded connections</strong></div></div><p className="he-boundary"><ShieldCheck size={20}/><span>{isRetail?"Prices can change with location, date and promotions.":"The model’s connections do not establish exact supplier allocation or a verified shipment route."}</span></p></section>}
 {tab==="journey"&&ingredientRecord&&<IngredientJourney key={ingredientRecord.cost_bucket_id} record={ingredientRecord} onCost={()=>setTab("cost")} onSources={()=>setTab("sources")}/>}
 {tab==="company"&&families.length===1&&<CompanyContext family={families[0]} data={data}/>}
 {tab==="cost"&&(isProcess?<CostNodePanel data={data} bucketId="COST_MANUFACTURING_CONVERSION"/>:<><p>Explore the existing estimate associated with this part of the journey. Shared allocations are counted once in the whole-bar model.</p><IngredientPanels key={node.id} data={data} initialFamily={families[0]} families={families}/></>)}
 {tab==="sources"&&<NodeResearch data={data} nodeId={node.id}/>}
 {tab==="connections"&&node.id&&<NodeConnections data={data} nodeId={node.id}/>}
 {tab==="process"&&node.id&&<ProcessStagePanel data={data} nodeId={node.id}/>}
 </div>;
}
