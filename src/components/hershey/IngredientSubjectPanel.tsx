"use client";
import {useState} from "react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import HomeIngredientDetail from "./HomeIngredientDetail";
import {SubjectGlass} from "./StoryObject";
import "./ingredient-panel-fit.css";
const groups=[{id:"cocoa",label:"Cocoa & chocolate",art:"cocoa",color:"#e1b77d"},{id:"sugar",label:"Sugar",art:"sugar",color:"#e5d29d"},{id:"dairy",label:"Milk & dairy",art:"dairy",color:"#a6dff5"},{id:"minor",label:"Smaller ingredients",art:"minor",color:"#c4a7e9"}] as const;
export default function IngredientSubjectPanel({data}:{data:EnrichedArtifacts}){const[selected,setSelected]=useState<(typeof groups)[number]["id"]>("cocoa"),group=groups.find(item=>item.id===selected)!;return <div className="ingredient-subject-panel"><div className="story-choices" role="group" aria-label="Ingredient stories">{groups.map(item=><button key={item.id} aria-pressed={selected===item.id} onClick={()=>setSelected(item.id)}><SubjectGlass name={item.art}/><span>{item.label}</span></button>)}</div><HomeIngredientDetail key={selected} data={data} family={selected} color={group.color}/></div>}
