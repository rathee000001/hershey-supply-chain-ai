"use client";
import NodeResearch from "./NodeResearch";
import StoryQuestions from "./StoryQuestions";
import SubjectIllustration from "./SubjectIllustration";
import {storyObjectFor} from "./StoryObject";
import {useState,type CSSProperties} from "react";
import {ArrowRight,Network,Coins,BookOpen,ShieldCheck} from "lucide-react";
import type {EnrichedArtifacts,GraphNode} from "@/lib/hershey/enrichedArtifacts";
import type {JourneyEdge} from "./scene-model";
import {HersheyOrb as Orb} from "./HersheyOrb";
import IngredientPanels from "./IngredientPanels";
import {familyForNode} from "./SupplySubjectDetail";
export default function SupplyConnectionDetail({data,edge,onSubject}:{data:EnrichedArtifacts;edge:JourneyEdge;onSubject:(node:GraphNode)=>void}){
 const[tab,setTab]=useState("story");
 const from=data.graph.nodes.find(n=>n.id===edge.source),to=data.graph.nodes.find(n=>n.id===edge.target);
 const underlying=(edge.sourceEdgeIds||[edge.id]).flatMap(id=>{const found=data.graph.edges.find(e=>e.id===id);return found?[found]:[]});
 const families=Array.from(new Set([...familyForNode(edge.source),...familyForNode(edge.target)]));
 const nodes=Array.from(new Set(underlying.flatMap(e=>[e.source,e.target]))).flatMap(id=>{const found=data.graph.nodes.find(n=>n.id===id);return found?[found]:[]});
 const documents=Array.from(new Map(nodes.flatMap(n=>n.enrichedEvidencePreview||[]).filter(e=>e.file_name&&e.public_display_allowed!==false).map(e=>[e.file_name!,e])).entries());
 return <div className="he-stories" data-selected="true" style={{"--story-tone":"#e8b48a"} as CSSProperties}>
 <StoryQuestions label="Connection detail views" value={tab} onChange={setTab} items={[
{id:"story",label:"The relationship",question:"How do these two subjects connect?",hint:"Follow the actual subjects and intermediate steps",art:"graph"},
{id:"cost",label:"Cost context",question:"Which estimates relate to this connection?",hint:"Shared allocations, counted once",art:"coins"},
{id:"sources",label:"The evidence",question:"What supports this part of the model?",hint:"Read the original source in this panel",art:"report"}]}/>
 {tab==="story"&&<section className="he-answer"><div className="ss-endpoints">{from&&<button onClick={()=>onSubject(from)}><SubjectIllustration name={storyObjectFor(from.id||"")||"research"} size={44}/>{from.label}</button>}<ArrowRight size={24}/>{to&&<button onClick={()=>onSubject(to)}><SubjectIllustration name={storyObjectFor(to.id||"")||"research"} size={44}/>{to.label}</button>}</div><h3>How these parts connect</h3><p>{edge.sourceEdgeIds?"This overview condenses intermediate steps so the whole journey is easier to follow. Open either subject above, or inspect the steps below.":"This link is part of the project's published supply-chain model. Its purpose is to explain the relationship between these two subjects."}</p><p className="he-boundary"><ShieldCheck size={20}/><span>Company relationships and modeled routes do not prove an exact supplier allocation or a tracked shipment for this bar.</span></p>{underlying.length>0&&<details><summary>{underlying.length===1?"Inspect the recorded connection":"See the steps inside this connection"}</summary><ol className="ss-connection-steps">{underlying.map(link=><li key={link.id}><strong>{data.graph.nodes.find(n=>n.id===link.source)?.label} → {data.graph.nodes.find(n=>n.id===link.target)?.label}</strong><p>{link.tooltipText}</p></li>)}</ol></details>}</section>}
 {tab==="cost"&&<><p>These estimates relate to the connected subjects. They are shared per-bar allocations—not extra costs to add each time a connection appears.</p><IngredientPanels data={data} initialFamily={families[0]} families={families}/></>}
 {tab==="sources"&&<section className="he-sources"><h3>Research around this connection</h3><p>Read the original documents connected to these subjects. They provide context, not automatic proof of this exact route.</p><NodeResearch data={data} nodeId={edge.source} evidenceIds={nodes.flatMap(node=>data.panelResearch.node_contexts[node.id||""]?.ordered_evidence_ids||[]).length?Array.from(new Set(nodes.flatMap(node=>data.panelResearch.node_contexts[node.id||""]?.ordered_evidence_ids||[]))):undefined}/></section>}
 </div>;
}
