"use client";
import {ArrowRight,Package,Factory,Truck,Warehouse,Store,Users,Blend,Waves,Snowflake,Shapes} from "lucide-react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
export function ProcessStepIcon({nodeId}:{nodeId:string}){const Icon=/MIXING/.test(nodeId)?Blend:/CONCHING/.test(nodeId)?Waves:/COOLING/.test(nodeId)?Snowflake:/MOLDING/.test(nodeId)?Shapes:/STORAGE/.test(nodeId)?Warehouse:/WRAPPING|GOODS/.test(nodeId)?Package:Factory;return <Icon size={18}/>;}
export default function HomeStageFlow({data,nodeId}:{data:EnrichedArtifacts;nodeId:string}){
 const node=data.graph.nodes.find(n=>n.id===nodeId),incoming=data.graph.edges.filter(e=>e.target===nodeId),outgoing=data.graph.edges.filter(e=>e.source===nodeId);
 const concise:Record<string,string>={NODE_SUPPLIER_ASR:"ASR",NODE_PACKAGING_STREAM:"Packaging",NODE_ING_SOY_LECITHIN:"Lecithin",NODE_COMMON_CARRIER_TRUCKING:"Carrier / trucking",NODE_PRODUCT_HERSHEY_155OZ:"Finished chocolate bar"};
 const label=(id?:string)=>id?(concise[id]||data.graph.nodes.find(n=>n.id===id)?.label):undefined;
 const incomingNames=Array.from(new Set(incoming.map(e=>label(e.source)).filter(Boolean))),outgoingNames=Array.from(new Set(outgoing.map(e=>label(e.target)).filter(Boolean)));
 const Icon=/MIXING/.test(nodeId)?Blend:/CONCHING/.test(nodeId)?Waves:/COOLING/.test(nodeId)?Snowflake:/MOLDING/.test(nodeId)?Shapes:/WAREHOUSE|STORAGE/.test(nodeId)?Warehouse:/CARRIER|MCLANE/.test(nodeId)?Truck:/RETAIL/.test(nodeId)?Store:/CONSUMER/.test(nodeId)?Users:/WRAPPING|GOODS/.test(nodeId)?Package:Factory;
 return <div className="ih-recorded-flow"><div className="ih-process-emblem" data-stage={nodeId}><Icon size={43}/><strong>{node?.label}</strong></div><div className="ih-input-output" data-many-inputs={incomingNames.length>3}><div><span>Arrives from</span>{incomingNames.length?incomingNames.map(name=><strong key={name}>{name}</strong>):<strong>No upstream link recorded</strong>}</div><ArrowRight size={22}/><div><span>Moves toward</span>{outgoingNames.length?outgoingNames.map(name=><strong key={name}>{name}</strong>):<strong>End of the modeled journey</strong>}</div></div><p>{node?.description}</p></div>;
}
