"use client";
import {useState} from "react";
import Link from "next/link";
import {Home,Network,FileSearch,Coins,BookOpen,Play,Menu} from "lucide-react";
import {OriginalGlassIconOrb} from "./reference/original-glass";
import ControlIcon,{type ControlIconName} from "./ControlIcon";
const navigation=[{name:"Home",href:"/",Icon:Home,color:"#83dfff"},{name:"Supply Chain",href:"/supply-chain",Icon:Network,color:"#a8ccfa"},{name:"Evidence",href:"/evidence-brain",Icon:FileSearch,color:"#91e4bb"},{name:"Cost Model",href:"/cost-model",Icon:Coins,color:"#edcb89"},{name:"Sources",href:"/sources",Icon:BookOpen,color:"#c8a8f0"},{name:"How It Works",href:"/methodology",Icon:Play,color:"#abc9ef"}];
export default function ProjectHeader({current}:{current:string}){const[open,setOpen]=useState(false);return <header className="ih-header"><Link href="/" className="ih-brand" aria-label="Hershey Supply Chain AI Home"><strong>HERSHEY’S</strong><span>SUPPLY CHAIN AI<small>AN INDEPENDENT STUDY</small></span></Link><button className="ih-menu" aria-label="Toggle navigation" aria-expanded={open} onClick={()=>setOpen(!open)}><Menu size={24}/></button><nav aria-label="Main navigation" data-open={open}>{navigation.map((item,index)=><Link key={item.href} href={item.href} aria-current={current===item.href?"page":undefined}><OriginalGlassIconOrb size={36} color={item.color} decorative><ControlIcon name={(["home","supply","evidence","cost","sources","how"] as ControlIconName[])[index]}/></OriginalGlassIconOrb>{item.name}</Link>)}</nav></header>}
