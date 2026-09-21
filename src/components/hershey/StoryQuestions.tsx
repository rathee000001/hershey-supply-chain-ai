"use client";
import type {CSSProperties} from "react";
import {ArrowUpRight} from "lucide-react";
import {HersheyOrb} from "./HersheyOrb";
import SubjectIllustration from "./SubjectIllustration";
import type {StoryObjectName} from "./StoryObject";
export type StoryQuestion={id:string;label:string;question:string;hint:string;art:StoryObjectName;color?:string};
/** Shared illustrated questions; the owning subject supplies its actual answer. */
export default function StoryQuestions({label,value,onChange,items}:{label:string;value:string;onChange:(id:string)=>void;items:StoryQuestion[]}){
 const selected=items.find(item=>item.id===value);
 return <div className="story-question-system" data-selected={Boolean(selected)}>
  <div className="story-question-choices" role="group" aria-label={label}>{items.map(item=><button type="button" key={item.id} aria-pressed={value===item.id} onClick={()=>onChange(item.id)} style={{"--question-tone":item.color||"#a5dcef"} as CSSProperties}><HersheyOrb size={42} color={item.color||"#a5dcef"} decorative><SubjectIllustration name={item.art} size={34}/></HersheyOrb><span><strong>{item.label}</strong><small>{item.hint}</small></span><ArrowUpRight size={14}/></button>)}</div>
  {selected&&<div className="story-question-heading"><SubjectIllustration name={selected.art} size={48}/><h3>{selected.question}</h3></div>}
 </div>;
}
