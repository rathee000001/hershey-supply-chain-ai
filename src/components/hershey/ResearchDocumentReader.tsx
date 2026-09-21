"use client";
import {useEffect,useRef,useState} from "react";
import dynamic from "next/dynamic";
import catalog from "@/lib/hershey/generated/document-catalog.json";
import {readDocumentRange} from "@/lib/hershey/documentTransport";
const PdfNotebook=dynamic(()=>import("./PdfNotebook"),{ssr:false,loading:()=> <p>Preparing the report reader…</p>});
export default function ResearchDocumentReader({fileName}:{fileName?:string;text?:string}){
 const entry=catalog.documents.find(item=>item.file_name===fileName);
 const host=useRef<HTMLDivElement>(null);
 const [visible,setVisible]=useState(false),[imageData,setImageData]=useState(""),[error,setError]=useState(""),[attempt,setAttempt]=useState(0);
 useEffect(()=>{const element=host.current;if(!element)return;const observer=new IntersectionObserver(entries=>{if(entries.some(item=>item.isIntersecting)){setVisible(true);observer.disconnect()}});observer.observe(element);return()=>observer.disconnect()},[]);
 useEffect(()=>{setImageData("");setError("");if(!visible||!entry?.media_type.startsWith("image/"))return;const controller=new AbortController();
  void (async()=>{const parts:Uint8Array[]=[];for(let begin=0;begin<entry.bytes;begin+=262144){const part=await readDocumentRange(entry.file_name,begin,Math.min(entry.bytes,begin+262144),controller.signal);parts.push(part.bytes)}const bytes=new Uint8Array(entry.bytes);let offset=0;for(const part of parts){bytes.set(part,offset);offset+=part.length}let binary="";for(const byte of bytes)binary+=String.fromCharCode(byte);if(!controller.signal.aborted)setImageData("data:"+entry.media_type+";base64,"+btoa(binary))})().catch(()=>{if(!controller.signal.aborted)setError("The original image could not be loaded. Please try again.")});return()=>controller.abort();
 },[visible,entry,attempt]);
 return <div className="research-notebook" ref={host}>
  <header><h3>Read the complete original</h3>{entry&&<a href={"/api/research-document?download=1&file="+encodeURIComponent(entry.file_name)} download={entry.file_name}>Download original</a>}</header>
  {!entry?<p role="status">This original is not available in the published collection. No excerpt is being substituted for it.</p>:!visible?<button className="hc-pill" onClick={()=>setVisible(true)}>Read document here</button>:entry.media_type.startsWith("image/")?error?<p role="alert">{error}</p>:imageData?<div className="original-source-image"><img src={imageData} alt={"Original source: "+entry.file_name} style={{width:"100%",height:"auto"}}/></div>:<p role="status">Preparing original image…</p>:<PdfNotebook key={entry.sha256+attempt} fileName={entry.file_name} title={entry.file_name}/>}
  {entry&&visible&&<button className="hc-pill" onClick={()=>setAttempt(value=>value+1)}>Reload reader</button>}
 </div>;
}
