export async function readDocumentRange(file:string,begin?:number,end?:number,signal?:AbortSignal){
 // PDF.js can coalesce several range chunks for a large embedded image.
 // Keep every network response bounded while returning that complete span.
 if(begin!==undefined&&end!==undefined&&end-begin>262144){
  const bytes=new Uint8Array(end-begin);let length=0,mediaType="";
  for(let offset=begin;offset<end;offset+=262144){const part=await readDocumentRange(file,offset,Math.min(end,offset+262144),signal);bytes.set(part.bytes,offset-begin);length=part.length;mediaType=part.mediaType}
  return {begin,end,length,mediaType,data:"",bytes};
 }
 const response=await fetch("/api/document-content",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({file,begin,end}),signal});
 if(!response.ok)throw new Error("Document data unavailable");
 const value=await response.json() as {begin:number;end:number;length:number;mediaType:string;data:string};
 return {...value,bytes:Uint8Array.from(atob(value.data),character=>character.charCodeAt(0))};
}
