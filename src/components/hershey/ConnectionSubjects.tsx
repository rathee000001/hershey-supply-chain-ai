import {ArrowRight} from "lucide-react";
import type {EnrichedArtifacts,GraphEdge} from "@/lib/hershey/enrichedArtifacts";
import StoryObject,{storyObjectFor} from "./StoryObject";
export default function ConnectionSubjects({data,edge}:{data:EnrichedArtifacts;edge?:GraphEdge}){
 if(!edge)return null;
 const nodes=[edge.source,edge.target].map(id=>data.graph.nodes.find(node=>node.id===id));
 return <div className="connection-subjects" aria-label="Subjects in the selected connection">{nodes.map((node,index)=><div className="connection-subject-slot" key={node?.id||index}><div className="connection-subject-picture" role="img" aria-label={`Illustration for ${node?.label||"subject"}`}><StoryObject name={storyObjectFor(node?.id||"")||(node?.type==="supplier"?"factory":node?.type==="distributor"?"warehouse":"research")}/></div><strong>{node?.label||"Subject not recorded"}</strong>{index===0&&<ArrowRight className="connection-subject-arrow" aria-hidden="true"/>}</div>)}</div>;
}
