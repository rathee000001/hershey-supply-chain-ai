"use client";
import {useEffect} from "react";
import {usePathname} from "next/navigation";
/** Keep page content below transparent navigation; the separate universe remains visible. */
export default function ReadingBoundary(){
 const pathname=usePathname();
 useEffect(()=>{let frame=0;const update=()=>{frame=0;const header=document.querySelector<HTMLElement>(".ih-header"),main=document.querySelector<HTMLElement>(".image-led-home main");if(!header||!main)return;const top=Math.max(0,header.getBoundingClientRect().bottom-main.getBoundingClientRect().top);main.style.clipPath=`inset(${top}px 0 0 0)`;};const schedule=()=>{if(!frame)frame=requestAnimationFrame(update)};schedule();window.addEventListener("scroll",schedule,{passive:true});window.addEventListener("resize",schedule);return()=>{cancelAnimationFrame(frame);window.removeEventListener("scroll",schedule);window.removeEventListener("resize",schedule);document.querySelector<HTMLElement>(".image-led-home main")?.style.removeProperty("clip-path")};},[pathname]);
 return null;
}
