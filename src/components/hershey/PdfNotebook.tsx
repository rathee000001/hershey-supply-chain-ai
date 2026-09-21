"use client";
import {useEffect,useRef,useState} from "react";
import type {PDFDocumentProxy,RenderTask} from "pdfjs-dist";
import {readDocumentRange} from "@/lib/hershey/documentTransport";
export default function PdfNotebook({fileName,title}:{fileName:string;title:string}){
 const [document,setDocument]=useState<PDFDocumentProxy|null>(null),[page,setPage]=useState(1),[zoom,setZoom]=useState(1),[error,setError]=useState(""),[busy,setBusy]=useState(true),[pageText,setPageText]=useState("");
 const canvas=useRef<HTMLCanvasElement>(null),viewport=useRef<HTMLDivElement>(null);
 const [readerWidth,setReaderWidth]=useState(0);
 useEffect(()=>{const element=viewport.current;if(!element)return;const observer=new ResizeObserver(()=>setReaderWidth(element.clientWidth));observer.observe(element);setReaderWidth(element.clientWidth);return()=>observer.disconnect()},[document,error]);
 useEffect(()=>{let cancelled=false;let dispose:(()=>void)|undefined;setBusy(true);setError("");setDocument(null);setPage(1);
  const controller=new AbortController();
  import("pdfjs-dist").then(async pdfjs=>{
   if(cancelled)return;
   pdfjs.GlobalWorkerOptions.workerSrc="/pdfjs/pdf.worker.min.mjs";
   const initial=await readDocumentRange(fileName,undefined,undefined,controller.signal);
   if(cancelled)return;
   let fail:(()=>void)|undefined;
   class ReaderRange extends pdfjs.PDFDataRangeTransport{
    requestDataRange(begin:number,end:number){
     void readDocumentRange(fileName,begin,end,controller.signal).then(part=>{if(!cancelled)this.onDataRange(begin,part.bytes)}).catch(()=>{if(!cancelled){setError("The document could not be loaded. Try reopening this reader.");setBusy(false);fail?.()}});
    }
    abort(){controller.abort()}
   }
   const range=new ReaderRange(initial.length,initial.bytes);
   const task=pdfjs.getDocument({range,rangeChunkSize:65536,disableStream:true,disableAutoFetch:true,cMapUrl:"/pdfjs/cmaps/",cMapPacked:true,standardFontDataUrl:"/pdfjs/standard_fonts/",wasmUrl:"/pdfjs/wasm/"});
   dispose=()=>{void task.destroy()};fail=dispose;
   const pdf=await task.promise;if(!cancelled)setDocument(pdf);
  }).catch(()=>{if(!cancelled){setError("The document could not be loaded. Try reopening this reader.");setBusy(false)}});
  return()=>{cancelled=true;controller.abort();dispose?.()};
 },[fileName]);
 useEffect(()=>{if(!document||!canvas.current||!viewport.current)return;let cancelled=false,render:RenderTask|undefined;setBusy(true);
  document.getPage(page).then(async sheet=>{if(cancelled||!canvas.current||!viewport.current)return;const target=canvas.current,base=sheet.getViewport({scale:1}),scale=Math.max(240,viewport.current.clientWidth-24)/base.width*zoom,view=sheet.getViewport({scale}),ratio=Math.min(window.devicePixelRatio||1,2);target.width=Math.ceil(view.width*ratio);target.height=Math.ceil(view.height*ratio);target.style.width=view.width+"px";target.style.height=view.height+"px";render=sheet.render({canvas:target,viewport:view,transform:[ratio,0,0,ratio,0,0]});await render.promise;const content=await sheet.getTextContent();if(!cancelled){setPageText(content.items.map(item=>"str"in item?item.str:"").join(" "));setBusy(false);}}).catch(e=>{if(!cancelled&&e?.name!=="RenderingCancelledException"){setError("This page could not be rendered. Try another page or reopen this reader.");setBusy(false)}});
  return()=>{cancelled=true;render?.cancel()};
 },[document,page,zoom,readerWidth]);
 return <div className="pdf-notebook"><div className="pdf-toolbar" role="group" aria-label="Report navigation"><button disabled={!document||page<=1} onClick={()=>setPage(p=>p-1)}>Previous page</button><label>Page <input aria-label="Report page" type="number" min={1} max={document?.numPages||1} value={page} onChange={e=>setPage(Math.max(1,Math.min(document?.numPages||1,Number(e.target.value)||1)))}/> of {document?.numPages||"…"}</label><button disabled={!document||page>=(document?.numPages||1)} onClick={()=>setPage(p=>p+1)}>Next page</button><select aria-label="Report zoom" value={zoom} onChange={e=>setZoom(Number(e.target.value))}><option value={1}>Fit width</option><option value={1.25}>125%</option><option value={1.5}>150%</option><option value={2}>200%</option></select></div>{error?<p role="alert">{error}</p>:<><p className="pdf-status" role="status">{busy?"Rendering report page…":`Original report · page ${page} of ${document?.numPages}`}</p><div className="pdf-page-viewport" ref={viewport}><canvas ref={canvas} role="img" aria-label={`${title}, original page ${page}`}/></div><details className="pdf-accessible-text"><summary>Read this page as text</summary><p>{pageText||"No extractable text is available on this page."}</p></details></>}</div>;
}
