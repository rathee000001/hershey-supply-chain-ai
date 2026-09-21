"use client";
import {useEffect} from "react";
/** Pointer-position reflections use the same material variables as the reference buttons. */
export default function GlassControlLighting(){
 useEffect(()=>{const move=(event:PointerEvent)=>{if(event.pointerType==="touch"||matchMedia("(prefers-reduced-motion: reduce)").matches)return;const target=event.target;if(!(target instanceof Element))return;const control=target.closest<HTMLElement>(".hc-home a,.hc-home button");if(!control||control.matches(".hf-node,.hf-edge")||control.closest('[data-motion-paused="true"]')||control.querySelector(".subject-glass"))return;const rect=control.getBoundingClientRect(),x=Math.max(0,Math.min(1,(event.clientX-rect.left)/rect.width)),y=Math.max(0,Math.min(1,(event.clientY-rect.top)/rect.height));control.style.setProperty("--orb-glint-angle",`${120+x*55}deg`);control.style.setProperty("--orb-light-x",`${20+x*30}%`);control.style.setProperty("--orb-light-y",`${12+y*20}%`);};document.addEventListener("pointermove",move,{passive:true});return()=>document.removeEventListener("pointermove",move)},[]);
 return null;
}
