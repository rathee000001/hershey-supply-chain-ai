import catalog from "@/lib/hershey/generated/document-catalog.json";

/** Names resolve only through the immutable exported public-document catalog. */
function documentResponse(request:Request){
 if(new URL(request.url).searchParams.get("download")!=="1")return Response.json({error:"Use the embedded reader. Original downloads require the dedicated download action."},{status:400});
 const name=new URL(request.url).searchParams.get("file");
 if(!name||/[\\\\/]/.test(name))return new Response(null,{status:400});
 const entry=catalog.documents.find(document=>document.file_name===name);
 if(!entry)return new Response(null,{status:404});
 // Static delivery preserves normal range requests without shipping the raw
 // research vault inside a serverless function.
 return Response.redirect(new URL(entry.public_url,request.url),307);
}
export async function GET(request:Request){return documentResponse(request);}
export async function HEAD(request:Request){return documentResponse(request);}
