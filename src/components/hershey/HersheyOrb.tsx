"use client";
import type {CSSProperties,ReactNode,PointerEvent} from "react";
import "./hershey-orb.css";

/** Hershey's optical sphere: one clear shell, atmospheric rim and contained subject. */
export function HersheyOrb({children,size=58,color="#7edfff",decorative=false,className="",label}:{children:ReactNode;size?:number;color?:string;decorative?:boolean;className?:string;label?:string}){
 const illuminate=(event:PointerEvent<HTMLSpanElement>)=>{const element=event.currentTarget;if(element.closest('[data-motion-paused="true"]')||matchMedia("(prefers-reduced-motion: reduce)").matches)return;const r=element.getBoundingClientRect();element.style.setProperty("--hershey-reflection-x",(20+(event.clientX-r.left)/r.width*25)+"%");element.style.setProperty("--hershey-reflection-y",(12+(event.clientY-r.top)/r.height*20)+"%");};
 return <span className={"hershey-orb "+className} style={{"--hershey-orb-size":size+"px","--hershey-orb-color":color} as CSSProperties} aria-hidden={decorative||undefined} aria-label={decorative?undefined:label} role={!decorative&&label?"img":undefined} onPointerMove={illuminate}><span className="hershey-orb-subject">{children}</span><span className="hershey-orb-reflection" aria-hidden="true"/></span>;
}
