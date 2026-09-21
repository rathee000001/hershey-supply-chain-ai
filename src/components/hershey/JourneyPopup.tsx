"use client";
import {useEffect,useRef,useState,type ReactNode} from "react";
import {X} from "lucide-react";
import {useSceneSession} from "./SceneSession";
import type {JourneyItem} from "./scene-model";
export type PopupDetail={title:string;content:ReactNode;companion?:ReactNode};
export default function JourneyPopup({detail,onClose,items=[],onSelect}:{detail:PopupDetail|null;onClose:()=>void;items?:JourneyItem[];onSelect?:(item:JourneyItem)=>void;art?:number}){
 const focus=useSceneSession(),panel=useRef<HTMLElement>(null),trigger=useRef<HTMLElement|null>(null),closeRef=useRef(onClose);
 closeRef.current=onClose;
 const [fallbackSide,setSide]=useState("right"),active=Boolean(detail);
 const side=focus.session?.side||fallbackSide;
 const [controlGroup,setControlGroup]=useState<Array<{label:string;element:HTMLButtonElement}>>([]);
 useEffect(()=>{if(!active)return;trigger.current=focus.session?.opener||document.activeElement as HTMLElement;const r=trigger.current?.getBoundingClientRect();setSide(focus.session?.side||(r&&r.left+r.width/2>innerWidth*.5?"left":"right"));window.scrollTo({top:scrollY,behavior:"instant"});const group=trigger.current?.closest("[data-detail-group],.hf-mobile-items,.rp-results,.rp-cost-rows,.rp-pipeline,.rp-inspector");setControlGroup(group?Array.from(group.querySelectorAll<HTMLButtonElement>("button")).map(element=>({element,label:element.innerText.replace(/\s+/g," ").trim()})).filter(c=>c.label):[]);const previous=document.body.style.overflow;document.body.style.overflow="hidden";document.documentElement.dataset.hersheyDetail="open";
 const blocks=Array.from(document.querySelectorAll<HTMLElement>(".hc-header,[data-story-section],#page-explorer,.hc-unified-footer,.hc-motion,.ih-header,.ih-hero-copy,.ih-stories,.ih-motion"));const before=blocks.map(e=>e.inert);blocks.forEach(e=>{e.inert=true});
 // The retained canvas is outside the dialog element and can sit above its
 // backdrop. Dismiss empty-space clicks there too, while preserving subjects,
 // connection targets, panel contents and genuine drag gestures.
 let outsidePress:{x:number;y:number}|null=null;
 const outside=(target:EventTarget|null)=>target instanceof Element&&!target.closest(".hj-popup>article,.hj-controls,.hj-record-context,.hf-node,.hf-edge-target,.hf-fallback");
 const pointerDown=(event:PointerEvent)=>{outsidePress=event.button===0&&outside(event.target)?{x:event.clientX,y:event.clientY}:null};
 const pointerUp=(event:PointerEvent)=>{if(outsidePress&&outside(event.target)&&Math.hypot(event.clientX-outsidePress.x,event.clientY-outsidePress.y)<6)closeRef.current();outsidePress=null};
 document.addEventListener("pointerdown",pointerDown,true);document.addEventListener("pointerup",pointerUp,true);
 const key=(e:KeyboardEvent)=>{if(e.key==="Escape"){e.preventDefault();closeRef.current();return}if(e.key!=="Tab")return;const list=Array.from(document.querySelectorAll<HTMLElement>(".hf-scene[data-detail-retained=true] button,.hj-popup button,.hj-popup a,.hj-popup summary,.hj-popup input,.hj-popup select,.hj-popup textarea,.hj-popup [tabindex]")).filter(el=>!el.hasAttribute("disabled")&&el.tabIndex>=0&&getComputedStyle(el).visibility!=="hidden"&&el.getClientRects().length);if(!list.length)return;const first=list[0],last=list[list.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}};
 window.addEventListener("keydown",key);const frame=requestAnimationFrame(()=>panel.current?.focus({preventScroll:true}));
 return()=>{cancelAnimationFrame(frame);window.removeEventListener("keydown",key);document.removeEventListener("pointerdown",pointerDown,true);document.removeEventListener("pointerup",pointerUp,true);document.body.style.overflow=previous;delete document.documentElement.dataset.hersheyDetail;blocks.forEach((e,i)=>{e.inert=before[i]});focus.close();requestAnimationFrame(()=>trigger.current?.focus({preventScroll:true}));};
 // Keep the opening composition frozen while selected content changes.
 // eslint-disable-next-line react-hooks/exhaustive-deps
 },[active]);
 if(!detail)return null;
 const retainScene=focus.session?.mode==="scene";
 return <div className="hj-popup" data-panel-side={side} data-has-scene={retainScene} role="dialog" aria-modal="true" aria-labelledby="journey-popup-title" aria-owns={retainScene?"retained-flow-scene":undefined}>
 {!retainScene&&detail.companion&&<aside className="hj-record-context" aria-label="Selected research context">{detail.companion}</aside>}
 {!retainScene&&controlGroup.length>0&&<aside className="hj-controls" aria-label="Opening control group">{controlGroup.map((control,i)=><button className="hc-pill" key={i} onClick={()=>control.element.click()}>{control.label}</button>)}</aside>}
 <article ref={panel} tabIndex={-1}><button className="hc-pill hj-close" aria-label="Close detail" onClick={onClose}><X size={18}/>Close</button><p className="hc-eyebrow">EXPLORE THE DETAIL</p><h2 id="journey-popup-title">{detail.title}</h2>{detail.content}</article>
 </div>
}
