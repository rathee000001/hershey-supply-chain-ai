import {readFile,mkdir,copyFile,stat} from "node:fs/promises";
import {createHash} from "node:crypto";
import {resolve,relative,dirname} from "node:path";
import {fileURLToPath} from "node:url";
import {writeFile} from "node:fs/promises";
const root=resolve(dirname(fileURLToPath(import.meta.url)),".."),vault=resolve(root,"data/raw_sources");
const inventory=JSON.parse(await readFile(resolve(root,"artifacts/00_source_inventory/source_inventory.json"),"utf8"));
const evidence=JSON.parse(await readFile(resolve(root,"public/data/hershey/enriched_display/enriched_evidence_panel_lookup_v2.json"),"utf8"));
const allowed=new Set(Object.values(evidence).filter(record=>record.public_display_allowed===true).map(record=>record.file_name));
const digest=bytes=>createHash("sha256").update(bytes).digest("hex"),documents=[],unique=new Map();
for(const name of [...allowed].sort()){
 const matches=inventory.filter(record=>record.file_name===name);if(matches.length!==1)throw Error("Ambiguous or missing original: "+name);
 const entry=matches[0],source=resolve(vault,entry.relative_path),rel=relative(vault,source);if(rel.startsWith("..")||resolve(vault,rel)!==source)throw Error("Source escaped vault");
 const bytes=await readFile(source),sha=digest(bytes),pdf=bytes.subarray(0,5).toString()==="%PDF-",png=bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]));
 if(!pdf&&!png)throw Error("Unsupported document type: "+name);
 if(entry.sha256&&entry.sha256!==sha)throw Error("Source inventory hash mismatch: "+name);
 const file=sha+(pdf?".pdf":".png"),url="/research-documents/"+file;
 documents.push({file_name:name,doc_id:entry.doc_id,sha256:sha,bytes:bytes.length,media_type:pdf?"application/pdf":"image/png",public_url:url});
 unique.set(file,{source,bytes:bytes.length,sha});
}
await mkdir(resolve(root,"public/research-documents"),{recursive:true});
for(const[file,entry]of unique){const destination=resolve(root,"public/research-documents",file);try{await stat(destination);if(digest(await readFile(destination))!==entry.sha)throw Error("Existing public document differs: "+file);}catch(error){if(error.code!=="ENOENT")throw error;await copyFile(entry.source,destination);}}
const catalog={version:"original_documents_v1",scope:"Original source documents referenced by public-display evidence, supplied for the requested full-document reader. Report contents are not blanket approval of every possible claim.",documents};
await mkdir(resolve(root,"src/lib/hershey/generated"),{recursive:true});
const output=JSON.stringify(catalog,null,2)+"\n";
await writeFile(resolve(root,"public/data/hershey/enriched_display/original_documents_v1.json"),output);
await writeFile(resolve(root,"src/lib/hershey/generated/document-catalog.json"),output);
console.log(JSON.stringify({source_names:documents.length,unique_assets:unique.size,total_bytes:[...unique.values()].reduce((sum,entry)=>sum+entry.bytes,0),largest_bytes:Math.max(...[...unique.values()].map(entry=>entry.bytes)),catalog_sha256:digest(output)},null,2));
