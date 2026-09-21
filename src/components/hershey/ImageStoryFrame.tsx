"use client";
import {useEffect,useState,type ReactNode} from "react";
import {Pause,Play,ArrowRight} from "lucide-react";
import {loadEnrichedArtifacts,type EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import ProjectHeader from "./ProjectHeader";
import ReferenceUniverse from "./ApprovedHomeUniverse";
import LivingFlowScene from "./LivingFlowScene";
import JourneyPopup,{type PopupDetail} from "./JourneyPopup";
import {useSceneSession} from "./SceneSession";
import type {JourneyChapter,JourneyItem} from "./scene-model";
import SiteFooter from "./SiteFooter";
import "./home-experience.css";
import "./section-journey.css";
import "./approved-home.css";
import "./image-led-home.css";
import "./image-story-frame.css";
export function useStoryData(){const[data,setData]=useState<EnrichedArtifacts|null>(null),[error,setError]=useState("");useEffect(()=>{let active=true;loadEnrichedArtifacts().then(value=>{if(active)setData(value)}).catch(()=>{if(active)setError("The published research could not load. Reload this page to retry.")});return()=>{active=false}},[]);return{data,error};}
export default function ImageStoryFrame({route,world,background,title,intro,eyebrow,sections,chapter,detail,onClose,onSelect,heroControls,children,error}:{route:string;world:string;background:string;title:[string,string];intro:string;eyebrow:string;sections:Array<{id:string;label:string}>;chapter:JourneyChapter;detail:PopupDetail|null;onClose:()=>void;onSelect:(item:JourneyItem)=>void;heroControls?:ReactNode;children:ReactNode;error?:string}){
 const[active,setActive]=useState(0),[paused,setPaused]=useState(false),[reduced,setReduced]=useState(false);const focus=useSceneSession();
 useEffect(()=>{const media=matchMedia("(prefers-reduced-motion: reduce)"),sync=()=>setReduced(media.matches);sync();media.addEventListener("change",sync);return()=>media.removeEventListener("change",sync)},[]);
 useEffect(()=>{const update=()=>{if(detail)return;let current=0;for(const[s,section]of sections.entries()){const box=document.getElementById(section.id)?.getBoundingClientRect();if(box&&box.top<=innerHeight*.4)current=s;}setActive(current)};update();window.addEventListener("scroll",update,{passive:true});return()=>window.removeEventListener("scroll",update)},[detail,sections]);
 return <div id="top" className={`hc-home image-led-home image-story-page ${world}-story-page`} data-active-section={active} data-motion-paused={paused||reduced}><ReferenceUniverse artPath={background} worldName={world} progress={active} paused={paused||reduced}/><a href="#story-main" className="hc-skip">Skip to content</a><ProjectHeader current={route}/>{!detail&&<nav className="ih-section-rail" aria-label={`${world} sections`}>{sections.map((s,i)=><a key={s.id} href={"#"+s.id} aria-current={active===i?"step":undefined}><span>{String(i).padStart(2,"0")}</span><b>{s.label}</b><i aria-hidden="true"/></a>)}</nav>}<main id="story-main"><section className="ih-hero" data-home-section id={sections[0].id}><div className="ih-hero-copy"><p className="ih-eyebrow">{eyebrow}</p><h1>{title[0]}<span>{title[1]}</span></h1><p className="ih-intro">{intro}</p>{heroControls}<a className="ih-primary" href={"#"+sections[1].id}>Explore the story <ArrowRight size={20}/></a>{error&&<p role="alert">{error}</p>}</div><div className="ih-scene" data-retained={Boolean(detail&&focus.session?.mode==="scene")} data-panel-side={focus.session?.side||"left"}><LivingFlowScene chapters={[chapter]} interactive={Boolean(children)} progress={0} connectionStyle="constellation" visible={active===0} paused={paused||reduced} onSelect={onSelect}/></div></section><div className="ih-stories">{children}</div></main><SiteFooter/><button className="ih-motion" aria-pressed={paused||reduced} disabled={reduced} onClick={()=>setPaused(value=>!value)}>{paused||reduced?<Play size={14}/>:<Pause size={14}/>} {reduced?"Reduced motion":paused?"Resume motion":"Pause motion"}</button><JourneyPopup detail={detail} onClose={onClose}/></div>;
}
