"use client";
import {useState} from "react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import HomeStageFlow,{ProcessStepIcon} from "./HomeStageFlow";
export default function ProcessStagePanel({data,nodeId}:{data:EnrichedArtifacts;nodeId:string}){const[selected,setSelected]=useState(nodeId),stages=data.graph.nodes.filter(node=>node.type==="manufacturing_process");return <section><p>Select a modeled stage to see its role, incoming materials and next connection. These are not proprietary production-line records.</p><div className="ih-process-picks" role="group" aria-label="Modeled production stages">{stages.map((stage,index)=><button key={stage.id} aria-label={stage.label} aria-pressed={selected===stage.id} onClick={()=>setSelected(stage.id!)}><ProcessStepIcon nodeId={stage.id!}/><span>{index+1}</span></button>)}</div><HomeStageFlow data={data} nodeId={selected}/></section>}
