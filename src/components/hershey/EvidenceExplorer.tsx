"use client";
import {useMemo,useState,type CSSProperties,type ReactNode} from "react";
import {Bean,Milk,Candy,FlaskConical,Package,Truck,Coins,Building2,BookOpen,ShieldCheck,Search,ArrowUpRight} from "lucide-react";
import type {EnrichedArtifacts,EvidencePreview} from "@/lib/hershey/enrichedArtifacts";
import {HersheyOrb as Orb} from "./HersheyOrb";
import "./evidence-explorer.css";
import ResearchDocumentReader from "./ResearchDocumentReader";
import SubjectIllustration from "./SubjectIllustration";
import type {StoryObjectName} from "./StoryObject";
const evidenceArt:Record<string,StoryObjectName>={cocoa:"cocoa",dairy:"dairy",sugar:"sugar",minor:"minor",product:"product",delivery:"truck",price:"coins",company:"factory"};

const subjects=[
 {id:"cocoa",name:"Cocoa & chocolate",hint:"Cocoa, chocolate and cocoa butter",packets:["cocoa_chocolate_cocoa_butter"],Icon:Bean,color:"#dcb58a"},
 {id:"dairy",name:"Milk & dairy",hint:"Milk, skim milk and milk fat",packets:["dairy_milk_skim_milk_milk_fat"],Icon:Milk,color:"#a6e3f4"},
 {id:"sugar",name:"Sugar",hint:"Sugar sourcing and context",packets:["sugar"],Icon:Candy,color:"#ead3a6"},
 {id:"minor",name:"Smaller ingredients",hint:"Lecithin, PGPR and natural flavor",packets:["soy_lecithin","pgpr","natural_flavor"],Icon:FlaskConical,color:"#c3abef"},
 {id:"product",name:"The bar & its packaging",hint:"Product identity and label research",packets:["product_sku_1_55oz","packaging_wrapper"],Icon:Package,color:"#a2ccf4"},
 {id:"delivery",name:"The journey to retail",hint:"Storage and distribution context",packets:["logistics_distribution"],Icon:Truck,color:"#93e1cd"},
 {id:"price",name:"Shelf prices",hint:"Recorded retailer observations",packets:["retail_price_evidence"],Icon:Coins,color:"#efd180"},
 {id:"company",name:"The wider company story",hint:"Company reporting and policies",packets:["hershey_company"],Icon:Building2,color:"#afbef5"},
];
type RecordEntry=EvidencePreview&{evidence_text?:string;entities?:string[];ingredients?:string[]};
const words=(value?:string)=>value?.replaceAll("_"," ")||"Not recorded";
export const documentTitle=(file?:string)=>!file?"Research document":/^\d/.test(file)?"Source image":file.replace(/\.[a-z0-9]+$/i,"").replaceAll("_"," ").replace(/\besg\b/gi,"sustainability").replace(/\bsku\b/gi,"product");
const roles:Record<string,string>={ingredient_confirmation:"Ingredient research",retail_price:"Shelf-price research",supplier_relationship:"Company relationship",cost_benchmark:"Cost benchmark",logistics_context:"Distribution research",manufacturing_process:"Manufacturing research",regulatory_context:"Regulatory context"};
export const evidenceHeading=(entry:EvidencePreview)=>roles[entry.primary_claim_role||""]||"Research context";
export function scopeExplanation(scope?:string){
 if(scope==="company_level_only")return "This record provides context about a company or its sourcing. It does not identify the supplier of an ingredient in this specific bar.";
 if(scope==="sku_or_label_level")return "This record is classified for product or label context. It does not establish a supplier allocation.";
 if(scope==="retail_page_level")return "This record is classified as a retailer-page observation. Price can vary by store, date and promotion; it does not establish profit.";
 if(/benchmark|cost/.test(scope||""))return "This record supports benchmark assumptions, not Hershey's internal invoices or actual production cost.";
 if(/logistics|route|industry/.test(scope||""))return "This record explains the wider process or distribution context. It does not verify a shipment route for this particular bar.";
 return "Read this record alongside its source. Its inclusion in the study is not proof of an exact supplier, route or internal cost.";
}

export function EvidenceRecordDetail({entry}:{entry:RecordEntry}){
 const[view,setView]=useState("meaning"),text=entry.evidence_text||entry.evidence_text_preview;
 return <div className="ee-detail"><div className="ee-detail-tabs" role="group" aria-label="Evidence detail views">{[{id:"meaning",label:"What it supports",Icon:ShieldCheck},{id:"source",label:"Read the source",Icon:BookOpen},{id:"record",label:"Research notes",Icon:Search}].map(item=><button key={item.id} aria-pressed={view===item.id} onClick={()=>setView(item.id)}><Orb size={39} color="#9ddfe8" decorative><item.Icon size={20}/></Orb>{item.label}</button>)}</div>
 {view==="meaning"?<section className="ee-meaning"><p className="hc-eyebrow">{evidenceHeading(entry)}</p><h3>{documentTitle(entry.file_name)}</h3><p>{scopeExplanation(entry.safe_scope)}</p><div className="ee-qualification"><ShieldCheck size={22}/><div><strong>Evidence strength: {words(entry.confidence_level)}</strong><p>This is the study's recorded assessment, not a guarantee that every possible interpretation is supported.</p></div></div><button className="hc-pill" onClick={()=>setView("source")}>Read the original report <ArrowUpRight size={16}/></button></section>:view==="source"?<section className="ee-source-text"><ResearchDocumentReader fileName={entry.file_name} text=""/></section>:<section className="ee-research-notes"><h3>How this record is qualified</h3><dl><div><dt>Scope recorded by the study</dt><dd>{words(entry.safe_scope)}</dd></div><div><dt>Source capture</dt><dd>{words(entry.source_type)}</dd></div><div><dt>Claim category</dt><dd>{words(entry.primary_claim_role)}</dd></div><div><dt>Evidence strength</dt><dd>{words(entry.confidence_level)}</dd></div></dl><details><summary>View the original research wording</summary><p>{entry.audited_safe_website_wording||"No interpretation note is available."}</p><small>Reference: {entry.evidence_id}</small></details></section>}
 </div>;
}

export function EvidenceContext({entry}:{entry:EvidencePreview}){const topic=subjects.find(item=>item.packets.includes(entry.packet||""));return <div className="ee-context-card"><Orb size={92} color={topic?.color||"#a2ddeb"} decorative><BookOpen size={44}/></Orb><p className="hc-eyebrow">{topic?.name||"Research context"}</p><h3>{documentTitle(entry.file_name)}</h3><p>{scopeExplanation(entry.safe_scope)}</p><span>Selected source context</span></div>;}
export default function EvidenceExplorer({data,open}:{data:EnrichedArtifacts;open:(title:string,content:ReactNode,companion?:ReactNode)=>void}){
 const[subject,setSubject]=useState(""),[query,setQuery]=useState(""),[confidence,setConfidence]=useState(""),[capture,setCapture]=useState(""),[limit,setLimit]=useState(12);
 const all=useMemo(()=>Object.values(data.evidence).filter(entry=>entry.public_display_allowed===true),[data]);
 const selected=subjects.find(item=>item.id===subject);
 const results=useMemo(()=>all.filter(entry=>(!selected||selected.packets.includes(entry.packet||""))&&(!confidence||entry.confidence_level===confidence)&&(!capture||entry.source_type===capture)&&[entry.file_name,entry.audited_safe_website_wording,entry.evidence_text,entry.evidence_text_preview,entry.packet].join(" ").toLowerCase().includes(query.toLowerCase())),[all,selected,confidence,capture,query]);
 const reset=()=>{setSubject("");setQuery("");setConfidence("");setCapture("");setLimit(12)};
 return <div className="ee-explorer"><p className="hc-eyebrow">FOLLOW YOUR QUESTION</p><h2>Explore the research by subject.</h2><p>Choose a part of the product story. Read what a record supports, then inspect its source.</p>
 <div className="ee-subjects" role="group" aria-label="Evidence subjects">{subjects.map(item=>{const count=all.filter(entry=>item.packets.includes(entry.packet||"")).length;return <button key={item.id} aria-pressed={subject===item.id} style={{"--evidence-tone":item.color} as CSSProperties} onClick={()=>{setSubject(subject===item.id?"":item.id);setLimit(12)}}><Orb size={51} color={item.color} decorative><SubjectIllustration name={evidenceArt[item.id]} size={43}/></Orb><strong>{item.name}</strong><small>{item.hint}</small><span>{count} research records</span></button>})}</div>
 <div className="ee-filters"><label className="ee-search"><Search size={21}/><input aria-label="Search evidence" placeholder="Search a subject, company or document…" value={query} onChange={e=>{setQuery(e.target.value);setLimit(12)}}/></label><label>Evidence strength<select value={confidence} onChange={e=>{setConfidence(e.target.value);setLimit(12)}}><option value="">All levels</option>{Array.from(new Set(all.map(entry=>entry.confidence_level).filter(Boolean))).map(value=><option key={value} value={value}>{words(value)}</option>)}</select></label><label>Source format<select value={capture} onChange={e=>{setCapture(e.target.value);setLimit(12)}}><option value="">All formats</option>{Array.from(new Set(all.map(entry=>entry.source_type).filter(Boolean))).map(value=><option key={value} value={value}>{value==="visual_ocr"?"Scanned or visual source":value==="text_or_table"?"Text or table":words(value)}</option>)}</select></label><button className="hc-pill" onClick={reset}>Reset</button></div>
 <p className="ee-result-count" role="status">{results.length} matching records{selected?" · "+selected.name:""}</p>
 <div className="ee-records">{results.slice(0,limit).map(entry=>{const topic=subjects.find(item=>item.packets.includes(entry.packet||""));const Icon=topic?.Icon||BookOpen;return <button key={entry.evidence_id} style={{"--evidence-tone":topic?.color||"#9cdbef"} as CSSProperties} onClick={()=>open(evidenceHeading(entry),<EvidenceRecordDetail key={entry.evidence_id} entry={entry}/>,<EvidenceContext entry={entry}/>)}><div className="ee-record-top"><Orb size={43} color={topic?.color||"#9cdbef"} decorative><SubjectIllustration name={topic?evidenceArt[topic.id]:"report"} size={36}/></Orb><span>{topic?.name||"Research"}</span></div><h3>{documentTitle(entry.file_name)}</h3><p>{scopeExplanation(entry.safe_scope)}</p><div className="ee-record-bottom"><span>{words(entry.confidence_level)} evidence strength</span><strong>Explore <ArrowUpRight size={15}/></strong></div></button>})}</div>
 {!results.length&&<div className="ee-empty"><h3>No matching research</h3><p>Try another phrase or reset the subject and filters.</p><button className="hc-pill" onClick={reset}>Show all subjects</button></div>}
 {results.length>limit&&<button className="hc-pill ee-more" onClick={()=>setLimit(limit+12)}>Show more research <ArrowUpRight size={17}/></button>}
 </div>;
}
