"use client";
import {useMemo,useState,type ReactNode,type CSSProperties} from "react";
import {Leaf,Factory,Truck,ShoppingBag,Coins,Search,ArrowUpRight,Package} from "lucide-react";
import type {EnrichedArtifacts,GraphNode} from "@/lib/hershey/enrichedArtifacts";
import {HersheyOrb as Orb} from "./HersheyOrb";
import SupplySubjectDetail from "./SupplySubjectDetail";
import IngredientPanels from "./IngredientPanels";
import "./supply-explorer.css";
const groups=[
 {id:"ingredients",title:"Ingredients & companies",question:"What goes into the bar?",Icon:Leaf,color:"#a1e7b7",types:["ingredient_origin","supplier","processor"]},
 {id:"making",title:"Making the chocolate",question:"How does the product take shape?",Icon:Factory,color:"#f0bf8a",types:["manufacturing_process","hershey_facility","visual_reference"]},
 {id:"delivery",title:"Storage & delivery",question:"How does it move onward?",Icon:Truck,color:"#9bd9ef",types:["warehouse","distributor"]},
 {id:"retail",title:"Retail & people",question:"Where does the journey lead?",Icon:ShoppingBag,color:"#d4b3ee",types:["retailer","consumer"]},
 {id:"cost",title:"Cost & price",question:"What contributes to the estimate?",Icon:Coins,color:"#edd089",types:["cost_bucket"]},
];
export default function SupplyExplorer({data,open}:{data:EnrichedArtifacts;open:(title:string,content:ReactNode)=>void}){
 const[group,setGroup]=useState("ingredients"),[query,setQuery]=useState("");
 const selected=groups.find(item=>item.id===group)!;
 const nodes=useMemo(()=>data.graph.nodes.filter(n=>(query.trim()||selected.types.includes(n.type||""))&&((n.label||"")+" "+(n.companyName||"")).toLowerCase().includes(query.trim().toLowerCase())),[data,selected,query]);
 const describe=(node:GraphNode)=>node.type==="supplier"?"Company sourcing context":node.type==="ingredient_origin"?"Ingredient origin and cost story":node.type==="manufacturing_process"?"Explore this manufacturing step":node.type==="retailer"?"Retail research and shelf price":node.type==="cost_bucket"?"Per-bar estimate and assumptions":"Explore the role, cost and evidence";
 return <div className="ss-explorer" style={{"--supply-tone":selected.color} as CSSProperties}>
 <p className="hc-eyebrow">CHOOSE A PART OF THE JOURNEY</p><h2>Explore the connected story.</h2><p>Start with a subject. Open its role, the related cost estimates and the research behind it.</p>
 <nav className="ss-groups" aria-label="Supply chain subjects">{groups.map(item=><button key={item.id} aria-pressed={group===item.id} onClick={()=>{setGroup(item.id);setQuery("")}} style={{"--supply-tone":item.color} as CSSProperties}><Orb size={42} color={item.color} decorative><item.Icon size={22}/></Orb><span>{item.title}</span></button>)}</nav>
 <label className="ss-search"><Search size={21}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Find cocoa, a company, a stage or a retailer…" aria-label="Search the supply chain"/>{query&&<button onClick={()=>setQuery("")} type="button">Clear</button>}</label>
 <h3>{query?"Search results":selected.question}</h3><p className="ss-count" role="status">{nodes.length} subjects to explore</p>
 <div className="ss-subjects">{nodes.map(node=>{const category=groups.find(item=>item.types.includes(node.type||""))||selected;const Icon=node.type==="visual_reference"?Package:category.Icon;return <button key={node.id} style={{"--supply-tone":category.color} as CSSProperties} onClick={()=>open(node.label||"Supply chain story",<SupplySubjectDetail key={node.id} data={data} node={node}/>)}><Orb size={53} color={category.color} decorative><Icon size={26}/></Orb><h4>{node.label}</h4><p>{describe(node)}</p><span>Explore <ArrowUpRight size={15}/></span></button>})}</div>
 {!nodes.length&&<div className="ss-empty"><p>No subjects match that search.</p><button className="hc-pill" onClick={()=>setQuery("")}>Show this group again</button></div>}
 <section className="ss-costs"><p className="hc-eyebrow">THE COST STORY</p><h2>What goes into one bar?</h2><p>Choose a group to explore the per-bar estimates. These are benchmark calculations, not company invoices; shared costs are counted once.</p><IngredientPanels data={data} initialFamily="cocoa" families={["sugar","cocoa","dairy","minor","packaging","manufacturing","logistics","retail","residual"]}/></section>
 </div>;
}
