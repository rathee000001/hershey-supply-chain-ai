"use client";
import {useEffect,useRef,useState,type CSSProperties} from "react";
import Image from "next/image";
import Link from "next/link";
import {Home,Network,FileSearch,Coins,BookOpen,Play,Pause,Menu,ArrowRight,ArrowUpRight,Bean,Milk,Candy,FlaskConical,Factory,Truck,Store,Users,Leaf,GraduationCap,ShieldCheck,Package} from "lucide-react";
import {loadEnrichedArtifacts,type EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import ReferenceUniverse from "./ApprovedHomeUniverse";
import LivingFlowScene from "./LivingFlowScene";
import {approvedHomeStory} from "./approved-home-story";
import {HersheyOrb} from "./HersheyOrb";
import StoryObject,{SubjectGlass,type StoryObjectName} from "./StoryObject";
import {useSceneSession} from "./SceneSession";
import JourneyPopup,{type PopupDetail} from "./JourneyPopup";
import type {JourneyItem} from "./scene-model";
import IngredientPanels,{formatCents,type FamilyName} from "./IngredientPanels";
import HomeProcessPanels from "./HomeProcessPanels";
import HomePeopleStory from "./HomePeopleStory";
import StoryQuestions from "./StoryQuestions";
import SubjectIllustration from "./SubjectIllustration";
import "./home-story-cards.css";
import ProjectHeader from "./ProjectHeader";
import CostNodePanel from "./CostNodePanel";
import IngredientSubjectPanel from "./IngredientSubjectPanel";
import SupplySubjectDetail from "./SupplySubjectDetail";
import HomeEvidenceStories from "./HomeEvidenceStories";
import SiteFooter from "./SiteFooter";
import HomeIngredientDetail from "./HomeIngredientDetail";
import HomeStageFlow,{ProcessStepIcon} from "./HomeStageFlow";
import HomeSubjectArtwork from "./HomeSubjectArtwork";
import "./home-experience.css";
import "./section-journey.css";
import "./approved-home.css";
import "./image-led-home.css";

const nav=[{name:"Home",href:"/",Icon:Home},{name:"Supply Chain",href:"/supply-chain",Icon:Network},{name:"Evidence",href:"/evidence-brain",Icon:FileSearch},{name:"Cost Model",href:"/cost-model",Icon:Coins},{name:"Sources",href:"/sources",Icon:BookOpen},{name:"How It Works",href:"/methodology",Icon:Play}];
const heroChapters=[approvedHomeStory[0]];
const origins=[
 {id:"cocoa",label:"Cocoa",Icon:Bean,color:"#e0b58b",x:18,y:19,description:"Explore chocolate, cocoa and cocoa butter together. Chocolate and cocoa share one cost bucket; cocoa butter is separate."},
 {id:"dairy",label:"Milk",Icon:Milk,color:"#9fdcf6",x:82,y:19,description:"Explore milk solids, skim milk and milk fat, with their separate quantity and price assumptions."},
 {id:"sugar",label:"Sugar",Icon:Candy,color:"#e9d6a4",x:18,y:77,description:"Follow the sugar research and see how the assumed quantity and benchmark price contribute to one bar."},
 {id:"minor",label:"Other ingredients",Icon:FlaskConical,color:"#c7a6ee",x:82,y:77,description:"Smaller inputs include lecithin, PGPR and natural flavor. Small quantities still have distinct assumptions and sources."},
] as const;
const stages=[{id:"making",label:"Manufacturing",Icon:Factory,color:"#efbf89"},{id:"delivery",label:"Distribution",Icon:Truck,color:"#97dbea"},{id:"retail",label:"Retail",Icon:Store,color:"#c7acf0"},{id:"people",label:"People",Icon:Users,color:"#8cd7ed"}] as const;

function IngredientStory({data,paused}:{data:EnrichedArtifacts;paused:boolean}){
 const[chosen,setChosen]=useState<FamilyName>("cocoa"),[showCalculation,setShowCalculation]=useState(false);
 const svg=useRef<SVGSVGElement>(null);
 useEffect(()=>{if(paused)svg.current?.pauseAnimations();else svg.current?.unpauseAnimations()},[paused]);
 const topic=origins.find(item=>item.id===chosen)!,value=data.calculationDetails.family_totals[chosen]?.base_cents_per_bar;
 return <section data-home-section className="ih-story-card" id="ingredient-origins"><div className="ih-card-heading"><span>01 / INGREDIENT ORIGINS</span><h2>Different ingredients.<br/>One connected story.</h2><p>Select an ingredient group to explore it here.</p></div>
 <div className="ih-origin-scene"><HomeSubjectArtwork cell={8} className="ih-origin-earth"/><svg ref={svg} viewBox="0 0 300 270" aria-hidden="true"><defs><radialGradient id="ih-globe"><stop offset="0" stopColor="#163860"/><stop offset=".75" stopColor="#081b35"/><stop offset="1" stopColor="#69bded"/></radialGradient><linearGradient id="ih-stream"><stop stopColor="#83d9fa"/><stop offset="1" stopColor="#c8a5ff"/></linearGradient></defs><circle cx="150" cy="130" r="77" fill="#081b35" stroke="#acecff" strokeWidth="1.2"/><ellipse cx="150" cy="130" rx="36" ry="77" fill="none" stroke="#8bcaf866"/><ellipse cx="150" cy="130" rx="66" ry="77" fill="none" stroke="#8bcaf844"/><ellipse cx="150" cy="130" rx="77" ry="27" fill="none" stroke="#8bcaf866"/><path d="M77 111Q150 77 223 111M77 148Q150 183 223 148" fill="none" stroke="#8bcaf844"/>{["M54 52Q80 90 150 130","M246 52Q220 90 150 130","M54 208Q86 159 150 130","M246 208Q215 158 150 130"].map((path,index)=><g key={path}><path d={path} stroke="url(#ih-stream)" strokeWidth="1.4" fill="none"/><circle r="2.5" fill="#e7faff"><animateMotion path={path} dur={4+index*.35+"s"} repeatCount="indefinite"/></circle></g>)}</svg>{origins.map(item=><button key={item.id} className="ih-origin" style={{left:item.x+"%",top:item.y+"%","--subject-color":item.color} as CSSProperties} aria-pressed={chosen===item.id} onClick={()=>{setChosen(item.id);setShowCalculation(false)}}><HersheyOrb size={61} color={item.color} decorative>{item.id==="minor"?<StoryObject name="minor"/>:<HomeSubjectArtwork cell={item.id==="cocoa"?0:item.id==="sugar"?1:2}/>}</HersheyOrb><span>{item.label}</span></button>)}<span className="ih-map-caption">Illustrative ingredient connections</span></div>
 <HomeIngredientDetail key={chosen} data={data} family={chosen} color={topic.color}/>
 </section>;
}

function FactoryStory({data}:{data:EnrichedArtifacts}){
 const[selected,setSelected]=useState("making"),[process,setProcess]=useState(0),[delivery,setDelivery]=useState("NODE_WAREHOUSE_DISTRIBUTION_CENTER");
 const current=stages.find(item=>item.id===selected)!,processes=data.graph.nodes.filter(node=>node.type==="manufacturing_process"),step=processes[process];
 const allocation=(family:string)=>data.calculationDetails.family_totals[family]?.base_cents_per_bar;
 return <section data-home-section className="ih-story-card" id="factory-to-shelf"><div className="ih-card-heading"><span>02 / FROM FACTORY TO SHOP SHELF</span><h2>Follow the making.<br/>Then the onward journey.</h2><p>Choose a stage. Its story stays in this section.</p></div>
 <div className="ih-stage-flow" role="group" aria-label="Factory to shelf stages">{stages.map((item,index)=><div className="ih-stage-slot" key={item.id}><button aria-pressed={selected===item.id} onClick={()=>setSelected(item.id)} style={{"--tone":item.color} as CSSProperties}><SubjectGlass name={(["factory","truck","retail","people"] as StoryObjectName[])[index]}/><span>{item.label}</span></button>{index<stages.length-1&&<ArrowRight className="ih-stage-arrow" size={20}/>}</div>)}</div>
 <div className="ih-inline-detail ih-stage-detail" style={{"--subject-color":current.color} as CSSProperties} aria-live="polite"><StoryQuestions label="Explore factory to shelf" value={selected} onChange={setSelected} items={[
{id:"making",label:"Manufacturing",question:"How do ingredients become a finished bar?",hint:"Follow the eight modeled steps",art:"factory"},
{id:"delivery",label:"Distribution",question:"How does the finished product move onward?",hint:"Separate storage from transport",art:"truck"},
{id:"retail",label:"Retail",question:"What did the shelf-price research find?",hint:"Compare the four recorded retailers",art:"retail"},
{id:"people",label:"People",question:"What does the shopper see at the end?",hint:"Connect the product, label and price",art:"people"}]}/>
 {selected==="making"?<><div className="ih-factory-art" aria-hidden="true"/><p>Ingredients come together through a modeled sequence of receiving, processing, cooling and wrapping.</p><div className="ih-process-picks" role="group" aria-label="Manufacturing steps">{processes.map((item,index)=><button key={item.id} onClick={()=>setProcess(index)} aria-pressed={process===index} aria-label={item.label}><ProcessStepIcon nodeId={item.id||""}/><span>{String(index+1).padStart(2,"0")}</span></button>)}</div>{step?.id&&<HomeStageFlow data={data} nodeId={step.id}/>}<div className="ih-inline-metric"><strong>{allocation("manufacturing")!=null?formatCents(allocation("manufacturing")):"Not available"}</strong><span>manufacturing allocation per bar</span></div><p className="ih-fine">One shared manufacturing estimate—not an extra charge for every stage. This is not a verified proprietary production line.</p></>:selected==="delivery"?<><HomeSubjectArtwork cell={5} className="ih-stage-illustration"/><div className="ih-delivery-picks" role="group" aria-label="Distribution stages">{data.graph.nodes.filter(n=>["warehouse","distributor"].includes(n.type||"")).map(n=><button key={n.id} aria-pressed={delivery===n.id} onClick={()=>setDelivery(n.id!)}>{n.label}</button>)}</div><HomeStageFlow data={data} nodeId={delivery}/><div className="ih-inline-metric"><strong>{allocation("logistics")!=null?formatCents(allocation("logistics")):"Not available"}</strong><span>storage and freight estimate per bar</span></div><p className="ih-fine">An illustrated route is not proof of a tracked shipment for this bar.</p><Link href="/supply-chain" className="ih-inline-action">Explore the full route <ArrowRight size={16}/></Link></>:selected==="retail"?<><div className="ih-retail-story-art" role="img" aria-label="Illustrative grocery store"><StoryObject name="retail"/></div><p>On the shelf, the same bar can have a different price from one retailer to another. Explore the four store observations recorded for this product.</p><div className="ih-retail-observations">{data.calculationDetails.verified_retailers.map(item=><div key={item.retailer}><span>{item.retailer}</span><strong>{formatCents(item.price_cents_per_bar)}</strong></div>)}</div><p className="ih-fine">Saved observations, not live prices. Store, date and promotions can change the amount.</p></>:<HomePeopleStory data={data}/>}
 </div></section>;
}

function AboutStory({data}:{data:EnrichedArtifacts}){
 const[view,setView]=useState("product");
 return <section data-home-section className="ih-story-card" id="about-the-study"><div className="ih-card-heading"><span>03 / ABOUT THIS STUDY</span><h2>A real product.<br/>A public-evidence study.</h2><p>See the scope, purpose and limits together.</p></div><div className="ih-about-product"><Image src="/home-art/product.png" width={420} height={280} alt="Illustration of a partly unwrapped milk chocolate bar"/></div><div className="ih-inline-detail">
 <StoryQuestions label="About this study" value={view} onChange={setView} items={[
 {id:"product",label:"The product",question:"What exactly is being studied?",hint:"One consistent unit for every comparison",art:"product"},
 {id:"purpose",label:"The purpose",question:"Why connect these sources?",hint:"An independent research explanation",art:"research"},
 {id:"limits",label:"The limits",question:"What must not be inferred?",hint:"Keep modeled estimates separate from proof",art:"audit"}]}/>
 {view==="product"?<><p>{data.manifest.unit}</p><p>The ingredient research, production model and cost comparison all return to this same product unit. A product label identifies ingredients; it does not identify which supplier provided them.</p></>:view==="purpose"?<><p>An independent project by Praveen Rathee, connecting ingredient research, supply-chain context and benchmark cost calculations.</p><p>Follow a subject into its relationships, inspect the assumptions behind a value, then read the original report alongside the study’s interpretation.</p></>:<><p>No exact supplier allocation, proprietary cost disclosure or tracked delivery route is inferred from a visual connection.</p><p>Saved retailer observations are not live prices. The difference between a cost estimate and shelf price is not a measured profit.</p></>}
 <div className="ih-about-links"><Link href="/sources">Explore sources <ArrowUpRight size={16}/></Link><Link href="/methodology">How the study works <ArrowUpRight size={16}/></Link></div></div></section>
}

export default function ImageLedHome(){
 const[data,setData]=useState<EnrichedArtifacts|null>(null),[error,setError]=useState(""),[retry,setRetry]=useState(0),[paused,setPaused]=useState(false),[reduced,setReduced]=useState(false),[menu,setMenu]=useState(false),[detail,setDetail]=useState<PopupDetail|null>(null),[heroVisible,setHeroVisible]=useState(true),[worldProgress,setWorldProgress]=useState(0),[activeSection,setActiveSection]=useState(0);
 const hero=useRef<HTMLElement>(null),focus=useSceneSession();
 useEffect(()=>{let active=true;setError("");loadEnrichedArtifacts().then(value=>{if(active)setData(value)}).catch(reason=>{if(active)setError(String(reason))});return()=>{active=false}},[retry]);
 useEffect(()=>{const media=matchMedia("(prefers-reduced-motion: reduce)"),sync=()=>setReduced(media.matches);sync();media.addEventListener("change",sync);return()=>media.removeEventListener("change",sync)},[]);
 useEffect(()=>{const observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.target===hero.current)setHeroVisible(entry.isIntersecting)},{threshold:0});if(hero.current)observer.observe(hero.current);return()=>observer.disconnect()},[]);
 useEffect(()=>{const update=()=>{if(detail)return;const sections=Array.from(document.querySelectorAll<HTMLElement>(".image-led-home [data-home-section]"));let current=0,progress=0;sections.forEach((section,index)=>{const r=section.getBoundingClientRect();if(r.top<=innerHeight*.35){current=index;progress=index+Math.min(.99,Math.max(0,(innerHeight*.35-r.top)/r.height))}});setActiveSection(current);setWorldProgress(Math.min(3,progress))};window.addEventListener("scroll",update,{passive:true});window.addEventListener("resize",update);update();return()=>{window.removeEventListener("scroll",update);window.removeEventListener("resize",update)}},[detail,data]);
 const inspect=(item:JourneyItem)=>{if(!data)return;const topic=item.id.slice(5);if(topic==="evidence"){setDetail({title:"The research behind the bar",content:<HomeEvidenceStories data={data}/>});return;}if(topic==="cost"){setDetail({title:"What contributes to the estimate?",content:<CostNodePanel key={topic} data={data}/>});return;}if(topic==="ingredients"){setDetail({title:"Explore the ingredients",content:<IngredientSubjectPanel data={data}/>});return;}const id=topic==="manufacturing"?"NODE_PROCESS_RECEIVING":topic==="distribution"?"NODE_WAREHOUSE_DISTRIBUTION_CENTER":"NODE_PRODUCT_HERSHEY_155OZ",node=data.graph.nodes.find(node=>node.id===id);if(node)setDetail({title:topic==="manufacturing"?"Inside the modeled process":topic==="distribution"?"From the factory toward the shelf":"One familiar product",content:<SupplySubjectDetail key={id} data={data} node={node}/>});};
 return <div id="top" className="hc-home image-led-home" data-active-section={activeSection} data-motion-paused={paused||reduced}><ReferenceUniverse progress={worldProgress} paused={paused||reduced}/><a href="#home-main" className="hc-skip">Skip to content</a>
 <ProjectHeader current="/"/>
 {!detail&&<nav className="ih-section-rail" aria-label="Home sections">{[{id:"overview",label:"Overview"},{id:"ingredient-origins",label:"Ingredient origins"},{id:"factory-to-shelf",label:"Factory to shelf"},{id:"about-the-study",label:"About this study"}].map((section,index)=><a key={section.id} href={"#"+section.id} aria-current={activeSection===index?"step":undefined}><span>{String(index).padStart(2,"0")}</span><b>{section.label}</b><i aria-hidden="true"/></a>)}</nav>}
 <main id="home-main"><section data-home-section ref={hero} className="ih-hero" id="overview" data-detail={Boolean(detail)}><div className="ih-hero-copy"><p className="ih-eyebrow">ONE PRODUCT. A CONNECTED WORLD.</p><h1>One bar.<span>A whole supply chain.</span></h1><p className="ih-intro">Follow the ingredients, the making and the journey to the shelf. Explore the research and estimated costs behind a familiar milk chocolate bar.</p><a className="ih-primary" href="#ingredient-origins">Explore the journey <ArrowRight size={22}/></a><div className="ih-principles"><span><Leaf size={22}/><b>REAL INGREDIENTS<small>Explore the inputs.</small></b></span><span><Network size={22}/><b>CONNECTED STAGES<small>Follow the journey.</small></b></span><span><BookOpen size={22}/><b>OPEN RESEARCH<small>Inspect the sources.</small></b></span></div>{!data&&<div className="ih-load" role={error?"alert":"status"}>{error?<><p>The research could not load.</p><button onClick={()=>setRetry(retry+1)}>Try again</button></>:"Loading the published research…"}</div>}</div>
 <div className="ih-scene" data-retained={Boolean(detail&&focus.session?.mode==="scene")} data-panel-side={focus.session?.side||"right"}><LivingFlowScene connectionStyle="constellation" homeModels chapters={heroChapters} progress={0} paused={paused||reduced} visible={heroVisible} interactive={Boolean(data)} onSelect={inspect}/></div></section>
 <section className="ih-stories" id="home-stories" aria-label="Explore the product story">{data?<><IngredientStory data={data} paused={paused||reduced}/><FactoryStory data={data}/><AboutStory data={data}/></>:<p className="ih-load">The story details appear when the research finishes loading.</p>}</section></main>
 <SiteFooter/><button className="ih-motion" disabled={reduced} aria-pressed={paused||reduced} onClick={()=>setPaused(!paused)}>{paused||reduced?<Play size={14}/>:<Pause size={14}/>} {reduced?"Reduced motion":paused?"Resume motion":"Pause motion"}</button>
 <JourneyPopup detail={detail} onClose={()=>setDetail(null)}/></div>;
}
