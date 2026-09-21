"use client";
import {documentIdentity} from "@/lib/hershey/documentIdentity";
import {useMemo,useState} from "react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import ResearchDocumentReader from "./ResearchDocumentReader";
import {documentTitle,scopeExplanation} from "./EvidenceExplorer";
export default function NodeResearch({data,nodeId,evidenceIds}:{data:EnrichedArtifacts;nodeId?:string;evidenceIds?:string[]}){
 const context=nodeId?data.panelResearch.node_contexts[nodeId]:undefined;
 const[mode,setMode]=useState(!evidenceIds&&context&&context.ordered_evidence_ids.length===0?"discovered":"linked"),[file,setFile]=useState(""),[reading,setReading]=useState(false),[page,setPage]=useState(0);
 const pageSize=3;
 const canSwitch=Boolean(context?.ordered_evidence_ids.length&&context.retrieved_document_context_ids.some(id=>!context.ordered_evidence_ids.includes(id)));
 const ids=evidenceIds||(mode==="linked"?context?.ordered_evidence_ids:context?.retrieved_document_context_ids)||[];
 const documents=useMemo(()=>{const groups=new Map<string,string[]>();for(const id of ids){const record=data.evidence[id];if(record?.public_display_allowed&&record.file_name)groups.set(documentIdentity(record.file_name),[...(groups.get(documentIdentity(record.file_name))||[]),id]);}return Array.from(groups,([identity,records])=>({name:data.evidence[records[0]].file_name!,records,identity}));},[data,ids]);
 const selected=documents.find(document=>document.name===file)||documents[0],entry=selected?data.evidence[selected.records[0]]:undefined;
 return <div className="node-research">{!evidenceIds&&canSwitch&&!reading&&<div className="ih-detail-tabs" role="group" aria-label="Research relationship"><button aria-pressed={mode==="linked"} onClick={()=>{setMode("linked");setPage(0);setReading(false);setFile("")}}>Linked research</button><button aria-pressed={mode==="discovered"} onClick={()=>{setMode("discovered");setPage(0);setReading(false);setFile("")}}>Related research</button></div>}
 {!reading&&<><p>{mode==="discovered"?"Related research located by the study’s index—not direct proof of this subject’s relationships.":"Read the original documents associated with this selection, with their recorded scope kept visible."}</p>
 <p className="ih-fine">{documents.length} documents · {ids.length} approved records{context&&!evidenceIds&&mode==="linked"?` · ${context.graph_assigned_evidence_ids.length} records directly assigned in the study`:""}</p></>}
 {reading&&selected?<><button className="hc-pill" onClick={()=>setReading(false)}>← Back to related documents</button><ResearchDocumentReader fileName={selected.name}/></>:<><div className="story-record-list">{documents.slice(page*pageSize,page*pageSize+pageSize).map(document=><button key={document.name} aria-pressed={selected?.name===document.name} onClick={()=>{setFile(document.name);setReading(true)}}><strong>{documentTitle(document.name)}</strong><small>{document.records.length} approved records · Open complete document →</small></button>)}</div>{!documents.length&&<p>No directly linked approved documents are recorded for this subject. The related-research view may provide background, but is not direct evidence of this modeled step.</p>}{documents.length>pageSize&&<div className="story-mini-actions"><button disabled={page===0} onClick={()=>setPage(value=>value-1)}>Previous</button><span>{page+1} / {Math.ceil(documents.length/pageSize)}</span><button disabled={(page+1)*pageSize>=documents.length} onClick={()=>setPage(value=>value+1)}>Next</button></div>}{entry&&<p className="ih-fine">{scopeExplanation(entry.safe_scope)}</p>}</>}
 </div>;
}
