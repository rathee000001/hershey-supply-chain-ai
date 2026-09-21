import catalog from "@/lib/hershey/generated/document-catalog.json";

export const runtime="nodejs";
/** Reader transport: JSON only, never redirects the browser to a PDF URL.
 * Originals remain static assets; each server response is bounded to 256 KiB. */
export async function POST(request:Request){
 let body:{file?:unknown;begin?:unknown;end?:unknown};
 try{body=await request.json()}catch{return Response.json({error:"Invalid request"},{status:400})}
 if(!body||typeof body!=="object"||typeof body.file!=="string")return Response.json({error:"Invalid document request"},{status:400});
 const entry=catalog.documents.find(item=>item.file_name===body.file);
 if(!entry)return Response.json({error:"Document not found"},{status:404});
 const begin=body.begin??0,end=body.end??Math.min(entry.bytes,65536);
 if(!Number.isSafeInteger(begin)||!Number.isSafeInteger(end)||typeof begin!=="number"||typeof end!=="number"||begin<0||end<=begin||end>entry.bytes||end-begin>262144)return Response.json({error:"Invalid page data range"},{status:400});
 // Only an allowlisted catalog path on our own deployment is ever fetched.
 const origin=process.env.VERCEL_PROJECT_PRODUCTION_URL?`https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`:new URL(request.url).origin;
 try{
  const response=await fetch(new URL(entry.public_url,origin),{headers:{Range:`bytes=${begin}-${end-1}`},cache:"no-store",signal:AbortSignal.timeout(20000)});
  if(response.status!==206){await response.body?.cancel();return Response.json({error:"Original document range unavailable"},{status:502})}
  const expected=`bytes ${begin}-${end-1}/${entry.bytes}`;
  if(response.headers.get("content-range")!==expected){await response.body?.cancel();return Response.json({error:"Original document range mismatch"},{status:502})}
  const bytes=Buffer.from(await response.arrayBuffer());
  if(bytes.length!==end-begin)return Response.json({error:"Incomplete document data"},{status:502});
  return Response.json({begin,end,length:entry.bytes,mediaType:entry.media_type,data:bytes.toString("base64")},{headers:{"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}});
 }catch{return Response.json({error:"The original document is temporarily unavailable"},{status:502})}
}
