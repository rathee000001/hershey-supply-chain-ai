"use client";
import {useState,type CSSProperties} from "react";
import {Bean,Milk,Candy,FlaskConical,Package,Factory,Truck,ShoppingBag,Coins,ArrowUpRight} from "lucide-react";
import type {EnrichedArtifacts,CostRecord} from "@/lib/hershey/enrichedArtifacts";
import "./ingredient-panels.css";
import CompanyContext from "./CompanyContext";
export const ingredientFamilies={
 sugar:{label:"Sugar",color:"#ecdab1",Icon:Candy},
 cocoa:{label:"Cocoa & chocolate",color:"#e1ac72",Icon:Bean},
 dairy:{label:"Milk & dairy",color:"#a6ddf4",Icon:Milk},
 minor:{label:"Minor ingredients",color:"#c3a5ef",Icon:FlaskConical},
 packaging:{label:"Packaging",color:"#84d8bd",Icon:Package},
 manufacturing:{label:"Manufacturing",color:"#e7b187",Icon:Factory},
 logistics:{label:"Storage & freight",color:"#82cfe8",Icon:Truck},
 retail:{label:"Retail observations",color:"#e6b6d3",Icon:ShoppingBag},
 residual:{label:"Channel / commercial gap",color:"#ccbee8",Icon:Coins}
};
export type FamilyName=keyof typeof ingredientFamilies;
export const formatCents=(value:number)=>new Intl.NumberFormat("en-US",{minimumFractionDigits:2,maximumFractionDigits:4}).format(value)+"¢";
export default function IngredientPanels({data,initialFamily="sugar",families=["sugar","cocoa","dairy","minor"],scenario:externalScenario,onScenarioChange}:{data:EnrichedArtifacts;initialFamily?:FamilyName;families?:FamilyName[];scenario?:"low"|"base"|"high";onScenarioChange?:(value:"low"|"base"|"high")=>void}){
 const [family,setFamily]=useState<FamilyName>(initialFamily),[selected,setSelected]=useState<string|null>(null),[localScenario,setLocalScenario]=useState<"low"|"base"|"high">("base");
 const scenario=externalScenario??localScenario,setScenario=onScenarioChange??setLocalScenario;
 const rows=data.costBreakdown.records?.filter(r=>r.safe_display===true&&r.family===family)||[];
 const theme=ingredientFamilies[family],chosen=rows.find(r=>r.cost_bucket_id===selected),key=(scenario+"_cents_per_bar") as "base_cents_per_bar";
 return <div className="hm-panels" style={{"--family-color":theme.color} as CSSProperties}>
 <nav className="hm-family-nav" aria-label="Ingredient and cost groups">{families.map(id=>{const group=ingredientFamilies[id];return <button key={id} onClick={()=>{setFamily(id);setSelected(null)}} aria-pressed={family===id} style={{"--family-color":group.color} as CSSProperties}><group.Icon size={23}/><span>{group.label}</span></button>})}</nav>
 <div className="hm-group-heading"><theme.Icon size={28}/><div><h3>{theme.label}</h3><p>Calculated cost per modeled bar</p></div><strong>{formatCents(data.calculationDetails.family_totals[family]?.[key]||0)}</strong></div>
 <div className="hm-scenarios" role="group" aria-label="Calculation scenario">{(["low","base","high"] as const).map(value=><button key={value} aria-pressed={scenario===value} onClick={()=>setScenario(value)}>{value[0].toUpperCase()+value.slice(1)}</button>)}</div>
 <div className="hm-card-grid">{rows.map(row=><button className="hm-mini-panel" key={row.cost_bucket_id} aria-expanded={chosen?.cost_bucket_id===row.cost_bucket_id} onClick={()=>setSelected(row.cost_bucket_id)}><theme.Icon size={27}/><h4>{row.label}</h4><strong>{formatCents(row[key])}</strong><span>per bar · {scenario} estimate</span><small>Open calculation <ArrowUpRight size={13}/></small></button>)}</div>
 {chosen&&<CalculationPanel record={chosen} scenario={scenario} data={data}/>}
 <CompanyContext key={family} data={data} family={family}/>
 {family==="cocoa"&&<p className="hm-boundary">Chocolate and Cocoa share one combined modeled cost bucket. Cocoa butter is separate.</p>}
 </div>;
}
export function CalculationPanel({record:r,scenario,data}:{record:CostRecord;scenario:"low"|"base"|"high";data:EnrichedArtifacts}){
 const inputs=r.calculation_inputs||{},grams=inputs["grams_"+scenario],price=inputs["price_"+scenario+"_per_lb"],key=(scenario+"_cents_per_bar") as "base_cents_per_bar";
 const evidence=(r.current_context_reference_ids||[]).map(id=>data.evidence[id]).filter(e=>e?.public_display_allowed===true);
 const files=Array.from(new Set(evidence.map(e=>e.file_name).filter(Boolean)));
 return <section className="hm-calculation" aria-label={r.label+" calculation"}><h3>{r.label}</h3><p>{r.cost_logic}</p>
 {typeof grams==="number"&&typeof price==="number"?<><div className="hm-input-pair"><div><span>Modeled quantity</span><strong>{grams} g</strong><small>per bar</small></div><div><span>Benchmark price</span><strong>${price.toFixed(2)}</strong><small>USD per pound</small></div></div><div className="hm-formula"><span>Existing backend formula</span><p>{grams} × ({price} ÷ 453.59237) × 100</p><strong>= {formatCents(r[key])} per bar</strong></div></>:<div className="hm-formula"><span>Recorded {scenario} allocation</span><strong>{formatCents(r[key])} per bar</strong></div>}
 <p>{r.notes}</p><p className="hm-confidence">Estimate confidence: {r.confidence_level?.replaceAll("_"," ")}</p>
 {files.length>0&&<details><summary>Related approved source context ({files.length} documents)</summary>{files.map(file=><p key={file}>{file?.replaceAll("_"," ")}</p>)}</details>}
 </section>
}
