"use client";
import {useState,type CSSProperties} from "react";
import Link from "next/link";
import {Package,Leaf,Truck,Coins,ShieldCheck,ArrowUpRight,BookOpen} from "lucide-react";
import {HersheyOrb as Orb} from "./HersheyOrb";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import {formatCents} from "./IngredientPanels";
import "./home-evidence-stories.css";
import NodeResearch from "./NodeResearch";
import SubjectIllustration from "./SubjectIllustration";
import type {StoryObjectName} from "./StoryObject";
const topicArt:Record<string,StoryObjectName>={bar:"product",ingredients:"cocoa",journey:"truck",price:"coins",trust:"audit"};
import "./panel-research.css";

const topics=[
 {id:"bar",title:"What's in the bar?",hint:"Start with the label",Icon:Package,color:"#96dcff",packets:["product_sku_1_55oz","packaging_wrapper"],summary:"The product label is the starting point for understanding this bar. It identifies the product and its listed ingredients; it does not identify the supplier behind each ingredient.",boundary:"A listed ingredient is not proof of who supplied it.",href:"/supply-chain",action:"Explore the ingredients"},
 {id:"ingredients",title:"Where do ingredients come from?",hint:"Explore the sourcing story",Icon:Leaf,color:"#a1e5bc",packets:["sugar","cocoa_chocolate_cocoa_butter","dairy_milk_skim_milk_milk_fat","natural_flavor","pgpr","soy_lecithin"],summary:"Public sourcing reports and ingredient research help explain the wider supply network. Read the cocoa, sugar and dairy stories while keeping company-wide relationships separate from this particular bar.",boundary:"The research does not trace every ingredient in this bar to an exact supplier or farm.",href:"/supply-chain",action:"Follow the supply chain"},
 {id:"journey",title:"How does it reach the shelf?",hint:"Follow the onward journey",Icon:Truck,color:"#c5b0ff",packets:["logistics_distribution"],summary:"Manufacturing, storage and distribution connect the product to retail. The project uses these stages to explain a possible route through the system, not to claim it tracked an individual shipment.",boundary:"An illustrated route is not a confirmed delivery route for this bar.",href:"/supply-chain",action:"Explore the journey"},
 {id:"price",title:"What explains the price?",hint:"Separate cost from shelf price",Icon:Coins,color:"#f1cd87",packets:["retail_price_evidence"],summary:"Ingredient and operating estimates describe the modeled physical cost. Separately collected retailer observations describe shelf prices. The difference includes more than profit.",boundary:"These are benchmark estimates, not Hershey's invoices. The remaining price gap is not a profit figure.",href:"/cost-model",action:"Explore the cost story"},
 {id:"trust",title:"What can we actually know?",hint:"See the limits as well as the evidence",Icon:ShieldCheck,color:"#aabfff",packets:["hershey_company"],summary:"This is an independent study built from public information. Product facts, wider company context and modeled estimates answer different questions; the interface should keep those differences visible.",boundary:"A public company report does not establish every supplier, process or cost for this exact product.",href:"/methodology",action:"How the study works"},
] as const;
const sourceTitle=(name:string)=>name.replace(/\.[a-z0-9]+$/i,"").replaceAll("_"," ").replace(/\bsku\b/gi,"product").replace(/\besg\b/gi,"sustainability");
export default function HomeEvidenceStories({data}:{data:EnrichedArtifacts}){
 const[selected,setSelected]=useState<string|null>(null),[showSources,setShowSources]=useState(false),[openSource,setOpenSource]=useState<string|null>(null);
 const topic=topics.find(item=>item.id===selected)||topics[0];
 const records=Object.values(data.evidence).filter(record=>record.public_display_allowed&&(topic.packets as readonly string[]).includes(record.packet||""));
 const documents=Array.from(new Map(records.filter(record=>record.file_name).map(record=>[record.file_name!,record])).entries());
 const physical=data.costBreakdown.physical_cost?.base_cents_per_bar;
 return <div className="he-stories" data-selected={Boolean(selected)} style={{"--story-tone":topic.color} as CSSProperties}>
 <p>Choose a question. Follow the story, then look at the sources behind it.</p>
 <div className="he-questions" role="group" aria-label="Questions about the chocolate bar">{topics.map((item,index)=><button key={item.id} aria-label={item.title} aria-pressed={selected===item.id} onClick={()=>{setSelected(item.id);setShowSources(false);setOpenSource(null)}} style={{"--story-tone":item.color} as CSSProperties}><Orb color={item.color} size={47} decorative><SubjectIllustration name={topicArt[item.id]} size={39}/></Orb><span><strong>{selected?["Product","Ingredients","Journey","Price","Scope"][index]:item.title}</strong><small>{item.hint}</small></span><ArrowUpRight size={16}/></button>)}</div>
 {selected&&<section className="he-answer" aria-live="polite"><div className="he-answer-heading"><Orb color={topic.color} size={61} decorative><SubjectIllustration name={topicArt[topic.id]} size={49}/></Orb><h3>{topic.title}</h3></div><p>{topic.summary}</p>
 {selected==="bar"&&<div className="he-fact"><SubjectIllustration name="product" size={42}/><span>{data.manifest.unit}</span></div>}
 {selected==="price"&&<div className="he-price-facts">{physical!=null&&<div><span>Modeled physical cost</span><strong>{formatCents(physical)}</strong><small>per bar · base estimate</small></div>}<div><span>Retail observations</span><strong>{data.calculationDetails.verified_retailers.length}</strong><small>separate retailer price records</small></div></div>}
 <p className="he-boundary"><ShieldCheck size={19}/><span>{topic.boundary}</span></p>
 <div className="he-actions"><Link className="hc-pill" href={topic.href}>{topic.action}<ArrowUpRight size={16}/></Link><button className="hc-text-link" aria-expanded={showSources} onClick={()=>setShowSources(!showSources)}><BookOpen size={17}/>{showSources?"Hide supporting sources":"Look at the sources"}</button></div>
 </section>}
 {showSources&&<section className="he-sources" aria-label="Supporting sources"><h3>Behind this story</h3><NodeResearch data={data} evidenceIds={records.map(record=>record.evidence_id!).filter(Boolean)}/></section>}
 </div>;
}
