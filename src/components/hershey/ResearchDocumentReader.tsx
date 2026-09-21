"use client";
import {useEffect,useState} from "react";
import dynamic from "next/dynamic";
import Image from "next/image";
const PdfNotebook=dynamic(()=>import("./PdfNotebook"),{ssr:false,loading:()=> <p>Preparing the report reader…</p>});
export default function ResearchDocumentReader({fileName}:{fileName?:string;text?:string}){
 const [available,setAvailable]=useState<boolean|null>(null);
 const [mediaType,setMediaType]=useState("");
 const url=fileName?"/api/research-document?file="+encodeURIComponent(fileName):"";
 useEffect(()=>{const controller=new AbortController();setAvailable(null);setMediaType("");if(!url){setAvailable(false);return;}fetch(url,{method:"HEAD",signal:controller.signal}).then(response=>{setMediaType(response.headers.get("content-type")||"");setAvailable(response.ok)}).catch(()=>{if(!controller.signal.aborted)setAvailable(false)});return()=>controller.abort();},[url]);
 return <div className="research-notebook" aria-busy={available===null}>
  <header><h3>{available?"Read the complete report":"Source notebook"}</h3>{available&&<a href={url} target="_blank" rel="noreferrer">Open full-size report ↗</a>}</header>
  {available===null?<p role="status">Opening the source document…</p>:available?mediaType.startsWith("image/")?<div className="original-source-image"><Image src={url} alt={"Original source image: "+fileName} width={1200} height={1600} unoptimized style={{width:"100%",height:"auto",objectFit:"contain"}}/></div>:<PdfNotebook key={url} url={url} title={fileName||"Research report"}/>:<p className="research-notebook-notice" role="status">The original document is not available in this copy of the site. A text extract is not being substituted for the report. Choose another document from the source collection.</p>}
 </div>;
}
