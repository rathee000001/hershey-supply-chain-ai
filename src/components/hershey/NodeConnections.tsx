"use client";
import {useState} from "react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import StoryQuestions from "./StoryQuestions";
import SubjectIllustration from "./SubjectIllustration";
import {storyObjectFor} from "./StoryObject";
export default function NodeConnections({data,nodeId}:{data:EnrichedArtifacts;nodeId:string}){
 const[page,setPage]=useState(0),[direction,setDirection]=useState("before");
 const edges=data.graph.edges.filter(edge=>direction==="before"?edge.target===nodeId:edge.source===nodeId);
 return <section><StoryQuestions label="Follow the recorded connections" value={direction} onChange={value=>{setDirection(value);setPage(0)}} items={[
 {id:"before",label:"Coming in",question:"What leads into this subject?",hint:"Follow the recorded upstream links",art:"packets"},
 {id:"after",label:"Moving on",question:"Where does the story go next?",hint:"Follow the recorded downstream links",art:"graph"}]}/>
 <p>{edges.length? `${edges.length} recorded ${edges.length===1?"connection":"connections"} in this direction. Follow the named subjects below to understand this part of the model.`:"The published graph records no connection in this direction. That is a limit of this model, not proof that no real-world relationship exists."}</p>
 <div className="panel-connected-edges">{edges.slice(page*3,page*3+3).map(edge=>{const from=data.graph.nodes.find(node=>node.id===edge.source),to=data.graph.nodes.find(node=>node.id===edge.target);return <div key={edge.id}><div className="connection-story-endpoints"><span><SubjectIllustration name={storyObjectFor(edge.source||"")||"research"} size={44}/><strong>{from?.label}</strong></span><b aria-hidden="true">→</b><span><SubjectIllustration name={storyObjectFor(edge.target||"")||"research"} size={44}/><strong>{to?.label}</strong></span></div><p>{edge.materialFlow||edge.tooltipText}</p><details><summary>What does this connection mean?</summary><p>{edge.tooltipText||"This is a relationship recorded in the study’s model."}</p><small>{edge.flowType?.replaceAll("_"," ")}</small></details></div>})}</div>
 <p className="ih-fine">These connections explain the published research model; they do not trace an individual bar or establish an exact supplier allocation.</p>
 {edges.length>3&&<div className="story-mini-actions"><button disabled={page===0} onClick={()=>setPage(value=>value-1)}>Previous</button><span>{page+1} / {Math.ceil(edges.length/3)}</span><button disabled={(page+1)*3>=edges.length} onClick={()=>setPage(value=>value+1)}>Next</button></div>}</section>
}
