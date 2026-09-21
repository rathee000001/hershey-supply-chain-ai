"use client";
import Link from "next/link";
import { useEffect,useMemo,useState } from "react";
import { ArrowRight,ArrowUpRight,BookOpen,Coins,FileSearch,Home,Menu,Network,Pause,Play } from "lucide-react";
import type { CSSProperties } from "react";
import { HersheyOrb as Orb } from "./HersheyOrb";
import { loadEnrichedArtifacts,type EnrichedArtifacts } from "@/lib/hershey/enrichedArtifacts";
import ApprovedHomeUniverse from "./ApprovedHomeUniverse";
import {approvedHomeStory} from "./approved-home-story";
import IngredientPanels,{formatCents} from "./IngredientPanels";
import HomeProcessPanels from "./HomeProcessPanels";
import HomeEvidenceStories from "./HomeEvidenceStories";
import "./approved-home.css";
import SiteFooter from "./SiteFooter";
import {useSceneSession} from "./SceneSession";
import SectionJourney,{buildJourney,type JourneyItem} from "./SectionJourney";
import JourneyPopup,{type PopupDetail} from "./JourneyPopup";
import "./home-experience.css";
import "./research-pages.css";
const nav=[["Home","/",Home,"#83dfff"],["Supply Chain","/supply-chain",Network,"#9bcbff"],["Evidence","/evidence-brain",FileSearch,"#8cebbd"],["Cost Model","/cost-model",Coins,"#e9c77e"],["Sources","/sources",BookOpen,"#c4a2ff"],["How It Works","/methodology",Play,"#a7c5fb"]] as const;
const pretty=(s?:string)=>s?.replaceAll("_"," ")||"Not recorded";
export default function HersheyHome(){
 const[data,setData]=useState<EnrichedArtifacts|null>(null),[error,setError]=useState(""),[paused,setPaused]=useState(false),[reduced,setReduced]=useState(false),[menu,setMenu]=useState(false),[progress,setProgress]=useState(0),[detail,setDetail]=useState<PopupDetail|null>(null);
 const sceneSession=useSceneSession();
 useEffect(()=>{let active=true;loadEnrichedArtifacts().then(d=>{if(active)setData(d)}).catch(e=>{if(active)setError(String(e))});return()=>{active=false}},[]);
 useEffect(()=>{const m=matchMedia("(prefers-reduced-motion: reduce)");const fn=()=>setReduced(m.matches);fn();m.addEventListener("change",fn);return()=>m.removeEventListener("change",fn)},[]);
 const chapters=approvedHomeStory;
 const select=(item:JourneyItem)=>{
  if(!data)return;
  if(item.id.startsWith("HOME:")){
   const topic=item.id.slice(5);
   if(topic==="study"){setDetail({title:"About this study",content:<><h3>A real product. A transparent study.</h3><p>Independent academic study by Praveen Rathee.</p><div className="hm-card-grid"><div className="hm-mini-panel"><h4>Product scope</h4><p>{data.manifest.unit}</p><p>Public-source research and benchmark estimates, not proprietary company cost disclosures.</p></div><div className="hm-mini-panel"><h4>Research context</h4><p>Source-backed ingredient, supply-chain and per-bar cost exploration. Company-level relationships do not prove allocation to this exact bar.</p></div></div><Link className="hc-pill" href="/methodology">How the study works</Link><Link className="hc-pill" href="/sources">Explore the sources</Link></>});return;}
   if(topic==="people"){setDetail({title:"The people at the end of the journey",content:<><p>This scene represents the shopper at the end of the modeled route. The research does not establish individual purchases or consumer behavior.</p><h3>What the project can show</h3><div className="hm-card-grid">{data.calculationDetails.verified_retailers.map(retailer=><div className="hm-mini-panel" key={retailer.retailer}><h4>{retailer.retailer.toUpperCase()}</h4><strong>{formatCents(retailer.price_cents_per_bar)}</strong><span>observed single-bar shelf price</span></div>)}</div><Link className="hc-pill" href="/cost-model">Understand shelf price and modeled cost</Link></>});return;}
   if(topic==="minor"){setDetail({title:"Other ingredients",content:<IngredientPanels key={item.id} data={data} initialFamily="minor" families={["minor"]}/>});return;}
   if(["ingredients","sugar","dairy","cost"].includes(topic)){
    setDetail({title:topic==="cost"?"What goes into the cost?":item.label,content:<IngredientPanels key={item.id} data={data} initialFamily={topic==="dairy"?"dairy":topic==="sugar"?"sugar":"cocoa"} families={topic==="cost"?["sugar","cocoa","dairy","minor","packaging","manufacturing","logistics","retail","residual"]:["sugar","cocoa","dairy","minor"]}/>});return;
   }
   if(topic==="manufacturing"){setDetail({title:"Manufacturing",content:<HomeProcessPanels data={data}/>});return;}
   if(topic==="distribution"||topic==="retail"){setDetail({title:"Distribution & retail",content:<><p>Individually verified single-bar observations from the project’s source records.</p><div className="hm-card-grid">{data.calculationDetails.verified_retailers.map(retailer=><div className="hm-mini-panel" key={retailer.retailer}><h4>{retailer.retailer.toUpperCase()}</h4><strong>{formatCents(retailer.price_cents_per_bar)}</strong><span>observed price per bar</span><small>{retailer.observation_date||"Observation date not captured"}</small></div>)}</div><IngredientPanels key={item.id} data={data} initialFamily="logistics" families={["logistics","retail","residual"]}/></>});return;}
   if(topic==="evidence"){setDetail({title:"The story behind the bar",content:<HomeEvidenceStories data={data}/>});return;}
   setDetail({title:"One milk chocolate bar",content:<><p>{data.manifest.unit}</p><p>An independent academic study by Praveen Rathee, connecting public research, a modeled supply chain and per-bar cost calculations.</p><p>Estimated physical cost: <strong>{formatCents(data.costBreakdown.physical_cost?.base_cents_per_bar||0)} per bar</strong>.</p><IngredientPanels key={item.id} data={data} initialFamily="cocoa"/></>});return;
  }
  if(item.id.startsWith("LIBRARY:")){setDetail({title:item.label,content:<><p>Explore the published research supporting this product model.</p><p>{Object.values(data.evidence).filter(e=>e.public_display_allowed).length} display-eligible evidence records.</p><Link className="hc-pill" href="/evidence-brain">Open evidence explorer</Link></>});return;}
  if(item.kind==="source"){const file=item.id.slice(4),entries=Object.values(data.evidence).filter(e=>e.public_display_allowed&&e.file_name===file);setDetail({title:file.replaceAll("_"," "),content:<><p>This document supports {entries.length} published evidence records.</p>{entries.map(e=><details key={e.evidence_id}><summary>{pretty(e.primary_claim_role)} · {pretty(e.safe_scope)}</summary><p>{e.audited_safe_website_wording}</p><blockquote>{e.evidence_text||e.evidence_text_preview}</blockquote></details>)}</>});return;}
  if(item.kind==="cost"){const r=data.costBreakdown.records?.find(r=>r.cost_bucket_id===item.id);if(r)setDetail({title:r.label,content:<><p>{r.cost_logic||r.notes}</p><dl className="rp-fields">{(["low","base","high"] as const).map(v=><div key={v}><dt>{v} estimate</dt><dd>{r[(v+"_cents_per_bar") as "base_cents_per_bar"].toFixed(2)}¢ per bar</dd></div>)}</dl><p>{r.notes}</p><Link className="hc-pill" href="/cost-model">Explore cost model <ArrowUpRight size={16}/></Link></>});return;}
  if(item.kind==="evidence"){const e=data.evidence[item.id];if(e)setDetail({title:e.file_name||"Source evidence",content:<><p>{e.audited_safe_website_wording}</p><p>Scope: {pretty(e.safe_scope)} · Confidence: {pretty(e.confidence_level)}</p><blockquote>{e.evidence_text||e.evidence_text_preview}</blockquote><Link className="hc-pill" href="/evidence-brain">Open evidence explorer</Link></>});return;}
  const ingredient=data.ingredients.find(i=>i.ingredient_id===(item.ingredientId||item.id)),node=data.graph.nodes.find(n=>n.id===item.id);
  if(!ingredient&&!node)return;
  const evidence=ingredient?.approved_evidence_preview||node?.enrichedEvidencePreview||[];
  setDetail({title:item.label,content:<><p>{ingredient?.origin_logic||node?.description}</p><dl className="rp-fields"><div><dt>Relationship</dt><dd>{pretty(ingredient?.supplier_status||node?.relationshipStatus)}</dd></div><div><dt>Confidence</dt><dd>{pretty(ingredient?.confidence_level||node?.confidenceLevel)}</dd></div></dl>{ingredient?.supplier_limitations?.map(s=><p key={s}>{s}</p>)}{node?.cost?.base!=null&&<p>Recorded base cost: {node.cost.base.toFixed(2)}¢ per bar.</p>}{evidence.map(e=><details key={e.evidence_id}><summary>{e.file_name}</summary><p>{e.audited_safe_website_wording}</p><blockquote>{e.evidence_text_preview}</blockquote></details>)}<Link className="hc-pill" href="/supply-chain">Explore the full network <ArrowUpRight size={17}/></Link></>});
 };
 const index=Math.min(chapters.length-1,Math.floor(progress));
 return <div id="top" className="hc-home approved-home" data-motion-paused={paused||reduced} data-active-chapter={index}>
 <ApprovedHomeUniverse progress={progress} paused={paused||reduced}/>
 <a className="hc-skip" href="#home-main">Skip to content</a>
 <header className="hc-header"><Link href="/" className="hc-brand" aria-label="Hershey Supply Chain AI Home"><strong>HERSHEY’S</strong><span>SUPPLY CHAIN AI<small>AN INDEPENDENT STUDY</small></span></Link><button className="hc-menu hc-pill" aria-label="Toggle navigation" aria-expanded={menu} onClick={()=>setMenu(!menu)}><Menu size={22}/></button><nav className={menu?"hc-nav is-open":"hc-nav"} aria-label="Main navigation">{nav.map(([label,url,Icon,color])=><Link className="hc-pill" key={url} href={url} aria-current={url==="/"?"page":undefined} style={{"--tone":color} as CSSProperties}><Orb color={color} size={33} decorative><Icon size={19}/></Orb>{label}</Link>)}</nav></header>
 <main id="home-main"><SectionJourney homeModels status={error?"error":data?"ready":"loading"} errorMessage={error} onRetry={()=>location.reload()} chapters={chapters} onSelect={select} onProgress={setProgress} paused={paused||reduced} detailOpen={!!detail} onEdge={edge=>setDetail({title:edge.materialFlow||"Connected context",content:<><p>{edge.tooltipText}</p><div className="hm-card-grid">{[edge.source,edge.target].map(id=>{const subject=chapters.flatMap(chapter=>chapter.items).find(item=>item.id===id);return subject?<button className="hm-mini-panel" key={id} onClick={()=>select(subject)}><strong>{subject.label}</strong><span>Open this subject’s evidence and detail →</span></button>:null})}</div><p>This connection guides exploration; it is not itself evidence of a verified commercial transaction.</p></>})}/>
 {error&&<p role="alert" className="hc-load">Research could not load. {error}<button onClick={()=>location.reload()}>Retry</button></p>}
 <section id="page-explorer" className="hc-home-end"><button className="hc-text-link" onClick={()=>setDetail({title:"About this study",content:<><p>Independent academic project by Praveen Rathee.</p><p>{data?.manifest.unit}</p><p>Public-source research and benchmark estimates. Not affiliated with, endorsed by or sponsored by The Hershey Company.</p><p>Source snapshot: {data?.manifest.created_at}</p></>})}>About this study <ArrowUpRight size={16}/></button></section>
 </main><button className="hc-motion hc-pill" aria-pressed={paused||reduced} disabled={reduced} onClick={()=>setPaused(!paused)}>{paused||reduced?<Play size={14}/>:<Pause size={14}/>} {reduced?"Reduced motion":paused?"Resume motion":"Pause motion"}</button>
 <SiteFooter/>
 <JourneyPopup detail={detail} onClose={()=>setDetail(null)} items={chapters[sceneSession.session?.chapter??index].items} onSelect={select} art={chapters[index].art}/>
 </div>
}
