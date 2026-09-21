"use client";
import {createContext,useContext,useState,useRef,type ReactNode,type RefObject} from "react";
import type {JourneyItem,OpeningPose} from "./scene-model";
type Session=OpeningPose&{opener:HTMLElement|null;mode:"scene"|"controls"};
type FlowTelemetry={samples:Array<{x:number;y:number}>;mix:number;progress:number};
const Context=createContext<{session:Session|null;flow:RefObject<FlowTelemetry>;open:(item:JourneyItem,element:HTMLElement,progress:number,chapter:number)=>void;close:()=>void}>({session:null,flow:{current:{samples:[],mix:0,progress:0}},open:()=>{},close:()=>{}});
export function SceneSessionProvider({children}:{children:ReactNode}){
 const[session,setSession]=useState<Session|null>(null);
 const flow=useRef<FlowTelemetry>({samples:[],mix:0,progress:0});
 const open=(item:JourneyItem,element:HTMLElement,progress:number,chapter:number)=>{
  const rect=element.getBoundingClientRect();
  const homeStory=element.closest("[data-story-section]");
  const rendered=element.closest<HTMLElement>(".hf-scene")||(homeStory?element.closest(".hc-home")?.querySelector<HTMLElement>(".hf-scene"):null);
  if(rendered){const p=Number(rendered.dataset.displayProgress),c=Number(rendered.dataset.displayChapter);if(Number.isFinite(p))progress=p;if(Number.isFinite(c))chapter=c;}
  window.scrollTo({top:scrollY,behavior:"instant"});
  const sceneRect=rendered?.getBoundingClientRect();
  const layoutCenter=sceneRect?sceneRect.left+sceneRect.width/2:rect.left+rect.width/2;
  setSession(previous=>previous?{...previous,subject:item}:{subject:item,opener:element,progress,chapter,side:layoutCenter>innerWidth*.5?"left":"right",origin:{x:rect.left+rect.width/2,y:rect.top+rect.height/2},mode:rendered?"scene":"controls"});
 };
 return <Context.Provider value={{session,flow,open,close:()=>setSession(null)}}>{children}</Context.Provider>;
}
export const useSceneSession=()=>useContext(Context);
