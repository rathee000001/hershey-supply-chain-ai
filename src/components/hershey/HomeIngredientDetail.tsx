"use client";
import {useState,type CSSProperties} from "react";
import Link from "next/link";
import {ArrowRight,BookOpen,Coins,Route,ShieldCheck} from "lucide-react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import {formatCents,type FamilyName} from "./IngredientPanels";
import NodeResearch from "./NodeResearch";
import "./panel-research.css";
const names:Record<string,string>={cocoa:"Cocoa & chocolate",dairy:"Milk & dairy",sugar:"Sugar",minor:"Other ingredients"};
const companies:Record<string,string>={cocoa:"SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE",dairy:"SUP_LAND_O_LAKES_DAIRY",sugar:"SUP_ASR_SUGAR"};
export default function HomeIngredientDetail({data,family,color}:{data:EnrichedArtifacts;family:FamilyName;color:string}){
 const records=(data.costBreakdown.records||[]).filter(r=>r.safe_display===true&&r.family===family),[selected,setSelected]=useState(records[0]?.cost_bucket_id),[tab,setTab]=useState("story");
 const record=records.find(r=>r.cost_bucket_id===selected)||records[0],company=data.suppliers.find(s=>s.supplier_packet_id===companies[family]&&s.display_allowed===true);
 if(!record)return <div className="ih-inline-detail">No published ingredient detail is available for this group.</div>;
 const story=record.ingredient_story,inputs=record.calculation_inputs||{},docs=Array.from(new Map((record.current_context_reference_ids||[]).map(id=>data.evidence[id]).filter(e=>e?.public_display_allowed===true&&e.file_name).map(e=>[e.file_name!,e])).entries());
 return <div className="ih-inline-detail ih-rich-detail" style={{"--subject-color":color} as CSSProperties} aria-live="polite"><div className="ih-rich-heading"><h3>{names[family]}</h3><strong>{formatCents(record.base_cents_per_bar)}<small>base estimate / bar</small></strong></div>
 {records.length>1&&<div className="ih-subingredient-picks" role="group" aria-label="Ingredients in this group">{records.map(r=><button key={r.cost_bucket_id} aria-pressed={record.cost_bucket_id===r.cost_bucket_id} onClick={()=>setSelected(r.cost_bucket_id)}>{r.label}</button>)}</div>}
 <div className="ih-detail-tabs" role="group" aria-label="Ingredient detail views">{[{id:"story",name:"The journey",Icon:Route},{id:"numbers",name:"Quantity & cost",Icon:Coins},{id:"sources",name:"Source context",Icon:BookOpen}].map(item=><button key={item.id} aria-pressed={tab===item.id} onClick={()=>setTab(item.id)}><item.Icon size={18}/>{item.name}</button>)}</div>
 {tab==="story"?<><h4>{record.label}</h4><p>{story?.origin||record.cost_logic}</p>{story?.process_steps?.length?<ol className="ih-material-flow">{story.process_steps.map((step,index)=><li key={index}><span>{step}</span>{index<story.process_steps.length-1&&<ArrowRight size={17}/>}</li>)}</ol>:null}<p className="ih-rich-limit"><ShieldCheck size={17}/><span>These are modeled ingredient paths. The study does not establish an exact supplier allocation to this bar.</span></p></>:tab==="numbers"?<><div className="ih-quantity-cards"><div><span>Modeled quantity</span><strong>{typeof inputs.grams_base==="number"?inputs.grams_base+" g":"Not specified"}</strong><small>in one 43 g bar</small></div><div><span>Benchmark price</span><strong>{typeof inputs.price_base_per_lb==="number"?"$"+inputs.price_base_per_lb.toFixed(2):"Not specified"}</strong><small>USD per pound</small></div><div><span>Estimated contribution</span><strong>{formatCents(record.base_cents_per_bar)}</strong><small>cents per bar</small></div></div><p>{record.cost_logic}</p><p className="ih-rich-limit">Published range: {formatCents(record.low_cents_per_bar)}–{formatCents(record.high_cents_per_bar)} per bar. This is not a company invoice.</p>{record.model_ingredient_id==="ING_COCOA_CHOCOLATE"&&<p className="ih-rich-limit">Chocolate and cocoa share this one modeled allocation; it is counted once.</p>}</>:<>{company&&<div className="ih-company-context"><span>Company-level research context</span><strong>{company.safe_display_name}</strong></div>}<NodeResearch data={data} nodeId={family==="cocoa"?"NODE_ORIGIN_COCOA":family==="dairy"?"NODE_ORIGIN_DAIRY":family==="sugar"?"NODE_ORIGIN_SUGAR":"NODE_"+record.model_ingredient_id}/></>}
 </div>;
}
