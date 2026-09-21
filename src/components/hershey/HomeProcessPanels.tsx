"use client";
import {useState,type CSSProperties} from "react";
import {Boxes,Warehouse,Blend,Waves,Shapes,Snowflake,Package,Factory,ArrowRight} from "lucide-react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import IngredientPanels from "./IngredientPanels";
const processIcons=[Boxes,Warehouse,Blend,Waves,Shapes,Snowflake,Package,Factory];
const colors=["#99d8ed","#a7bdf5","#d3adeb","#e8b08a","#e5c17f","#9ee6ef","#9cdcc0","#c8c1f3"];
export default function HomeProcessPanels({data}:{data:EnrichedArtifacts}){
 const stages=data.graph.nodes.filter(node=>node.type==="manufacturing_process");
 const[selected,setSelected]=useState(stages[0]?.id);
 const active=stages.find(node=>node.id===selected),index=stages.findIndex(node=>node.id===selected),color=colors[Math.max(0,index)%colors.length];
 return <div className="hm-process" style={{"--family-color":color} as CSSProperties}>
 <p>Explore each modeled production stage. This explains a chocolate-making process; it is not a verified proprietary production line for this exact bar.</p>
 <div className="hm-process-stages" role="group" aria-label="Manufacturing stages">{stages.map((stage,i)=>{const Icon=processIcons[i%processIcons.length];return <button key={stage.id} aria-pressed={selected===stage.id} onClick={()=>setSelected(stage.id)} style={{"--family-color":colors[i%colors.length]} as CSSProperties}><Icon size={24}/><span>{stage.label}</span><ArrowRight size={14}/></button>})}</div>
 {active&&<section className="hm-calculation" aria-live="polite"><h3>{active.label}</h3><p>{active.description}</p><p className="hm-boundary">Relationship: {active.relationshipStatus?.replaceAll("_"," ")||"Not recorded"}</p><p className="hm-confidence">Confidence: {active.confidenceLevel?.replaceAll("_"," ")||"Not recorded"}</p>{active.enrichedEvidencePreview?.map(record=><details key={record.evidence_id}><summary>{record.file_name?.replaceAll("_"," ")||"Related source"}</summary><p>{record.audited_safe_website_wording}</p><blockquote>{record.evidence_text_preview}</blockquote></details>)}</section>}
 <h3>Manufacturing and packaging allocations</h3><p>These are stage-level benchmark allocations, not separate costs for every process step.</p>
 <IngredientPanels data={data} initialFamily="manufacturing" families={["manufacturing","packaging"]}/>
 </div>;
}
