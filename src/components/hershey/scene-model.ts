import type { EnrichedArtifacts, GraphEdge } from "@/lib/hershey/enrichedArtifacts";
import type {StoryObjectName} from "./StoryObject";
export type JourneyItem={id:string;label:string;kind:"node"|"ingredient"|"cost"|"evidence"|"method"|"source";color:string;tag?:string;summary?:string;ingredientId?:string;logoUrl?:string;artwork?:StoryObjectName;core?:boolean;position?:{x:number;y:number}};
export type JourneyEdge=GraphEdge&{id:string;source:string;target:string;presentation?:boolean;sourceEdgeIds?:string[]};
export type JourneyChapter={label:string;title:string;body:string;art:number;pattern:"orbit"|"converge"|"process"|"route"|"layers"|"library";items:JourneyItem[];edges:JourneyEdge[]};
export type OpeningPose={side:"left"|"right";progress:number;chapter:number;subject:JourneyItem;origin:{x:number;y:number};};
export const scenePalette=["#91dfec","#b9a8e6","#e3c28e","#8fd6b7","#a7c6e5"];
const ingredientCrosswalk:Record<string,string>={NODE_ORIGIN_SUGAR:"ING_SUGAR",NODE_ORIGIN_COCOA:"ING_COCOA",NODE_ORIGIN_DAIRY:"ING_MILK",NODE_ING_SOY_LECITHIN:"ING_SOY_LECITHIN",NODE_ING_PGPR:"ING_PGPR",NODE_ING_NATURAL_FLAVOR:"ING_NATURAL_FLAVOR"};
const names:Record<string,string>={NODE_PRODUCT_HERSHEY_155OZ:"The milk chocolate bar",NODE_ORIGIN_SUGAR:"Sugar origins",NODE_ORIGIN_COCOA:"Cocoa origins",NODE_ORIGIN_DAIRY:"Dairy origins",NODE_PROCESS_RECEIVING:"Raw materials",NODE_PROCESS_STORAGE:"Ingredient storage",NODE_PROCESS_MIXING_REFINING:"Mixing & refining",NODE_PROCESS_CONCHING:"Conching",NODE_PROCESS_TEMPERING_MOLDING:"Tempering & molding",NODE_PROCESS_COOLING:"Cooling",NODE_PROCESS_WRAPPING:"Wrapping",NODE_PROCESS_FINISHED_GOODS:"Finished bars",NODE_WAREHOUSE_DISTRIBUTION_CENTER:"Warehouse",NODE_COMMON_CARRIER_TRUCKING:"Freight",NODE_DISTRIBUTOR_MCLANE:"McLane",NODE_SUPPLIER_ASR:"ASR",NODE_SUPPLIER_BARRY:"Barry Callebaut",NODE_SUPPLIER_LAND_O_LAKES:"Land O’Lakes"};
const filenameLabel=(name:string)=>name.replace(/\.pdf$/i,"").replace(/^hershey_/i,"").replace(/latest_esg_/i,"ESG — ").replaceAll("_"," ");
export function buildJourney(data:EnrichedArtifacts|null,kind:string,scenario:"low"|"base"|"high"="base"):JourneyChapter[]{
 const palette=scenePalette;
 const companyAssets:Record<string,[string,string]>={NODE_SUPPLIER_ASR:["SUP_ASR_SUGAR","asr_logo.svg"],NODE_SUPPLIER_BARRY:["SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE","barry_callebaut_logo.svg"],NODE_SUPPLIER_LAND_O_LAKES:["SUP_LAND_O_LAKES_DAIRY","land_olakes_logo.png"],NODE_DISTRIBUTOR_MCLANE:["SUP_MCLANE_DISTRIBUTION","mclane_logo.svg"]};
 const node=(id:string,i:number,core=false):JourneyItem|undefined=>{const n=data?.graph.nodes.find(n=>n.id===id),asset=companyAssets[id],allowed=asset&&data?.suppliers.some(s=>s.supplier_packet_id===asset[0]&&s.display_allowed===true&&s.logo_allowed===true);return n?{id,label:names[id]||n.label||id,kind:"node",color:palette[i%5],ingredientId:ingredientCrosswalk[id],logoUrl:allowed?"/data/hershey/visual_assets/source_assets/"+asset[1]:undefined,summary:n.hoverSummary||n.description,core}:undefined};
 const pick=(ids:string[],core?:string)=>ids.map((id,i)=>node(id,i,id===core)).filter((n):n is JourneyItem=>!!n);
 const product="NODE_PRODUCT_HERSHEY_155OZ",receiving="NODE_PROCESS_RECEIVING";
 const graphEdges:JourneyEdge[]=data?.graph.edges.filter(e=>e.id&&e.source&&e.target).map(e=>({...e,id:e.id!,source:e.source!,target:e.target!}))||[];
 const upstream=pick(["NODE_ORIGIN_SUGAR","NODE_SUPPLIER_ASR","NODE_ORIGIN_COCOA","NODE_SUPPLIER_BARRY","NODE_ORIGIN_DAIRY","NODE_SUPPLIER_LAND_O_LAKES",receiving],receiving);
 const minor=pick(["NODE_ING_SOY_LECITHIN","NODE_ING_PGPR","NODE_ING_NATURAL_FLAVOR","NODE_PACKAGING_STREAM",receiving],receiving);
 const process=pick(["NODE_HERSHEY_MANUFACTURING",...(data?.graph.nodes.filter(n=>n.type==="manufacturing_process").map(n=>n.id!)||[]),product],"NODE_HERSHEY_MANUFACTURING");
 const downstream=pick([product,...(data?.graph.nodes.filter(n=>["warehouse","distributor","retailer","consumer"].includes(n.type||"")).map(n=>n.id!)||[])],product);
 const overview=pick([product,"NODE_PROCESS_FINISHED_GOODS","NODE_WAREHOUSE_DISTRIBUTION_CENTER","NODE_COST_INGREDIENTS","NODE_COST_PACKAGING","NODE_COST_RETAIL"],product);
 const records=(data?.costBreakdown.records||[]).filter(r=>r.safe_display===true);
 const costLabels:Record<string,string>={COST_ING_SUGAR:"Sugar",COST_ING_COCOA_CHOCOLATE:"Chocolate / cocoa",COST_ING_COCOA_BUTTER:"Cocoa butter",COST_ING_MILK:"Milk solids",COST_ING_SKIM_MILK:"Skim milk",COST_ING_MILK_FAT:"Milk fat",COST_ING_SOY_LECITHIN:"Lecithin",COST_ING_PGPR:"PGPR",COST_ING_NATURAL_FLAVOR:"Natural flavor",COST_PACKAGING_PRIMARY_SECONDARY:"Packaging",COST_MANUFACTURING_CONVERSION:"Manufacturing",COST_STORAGE_WAREHOUSING:"Warehousing",COST_OUTBOUND_FREIGHT:"Freight",COST_RETAIL_PRICE_VERIFIED:"Shelf price",COST_RESIDUAL_CHANNEL_COMMERCIAL_POOL:"Commercial gap"};
 const costItems=(types:string[])=>records.filter(r=>types.includes(r.cost_type)).map((r,i):JourneyItem=>({id:r.cost_bucket_id,label:costLabels[r.cost_bucket_id]||r.label,kind:"cost",color:palette[i%5],tag:r[(scenario+"_cents_per_bar") as "base_cents_per_bar"].toFixed(2)+"¢ "+scenario}));
 const costs=costItems(["packaging","manufacturing_conversion","storage","freight"]);
 const ingredientCosts=costItems(["ingredient"]);
 const retail=costItems(["retail_price","residual_channel_pool"]);
 const evidence=Object.values(data?.evidence||{}).filter(e=>e.public_display_allowed===true);
 const selectedEvidence:typeof evidence=[];const selectedPackets=new Set<string>(),selectedFiles=new Set<string>();
 for(const entry of evidence){if(!entry.file_name||selectedPackets.has(entry.packet||"")||selectedFiles.has(entry.file_name))continue;selectedEvidence.push(entry);selectedPackets.add(entry.packet||"");selectedFiles.add(entry.file_name);if(selectedEvidence.length===4)break}
 const topicArtwork=(packet:string):StoryObjectName=>/sugar/.test(packet)?"sugar":/dairy|milk/.test(packet)?"dairy":/cocoa/.test(packet)?"cocoa":/retail/.test(packet)?"retail":/logistic/.test(packet)?"truck":/packaging|sku/.test(packet)?"packaging":"research";
 const topicName=(packet:string)=>/sugar/.test(packet)?"Sugar research":/dairy|milk/.test(packet)?"Dairy research":/cocoa/.test(packet)?"Cocoa research":/retail/.test(packet)?"Retail observations":/logistic/.test(packet)?"Distribution context":"Product research";
 const docs=selectedEvidence.map((e,i):JourneyItem=>({id:"DOC:"+e.file_name,label:filenameLabel(e.file_name||"Document"),kind:"source",color:palette[i%5],artwork:/agreement|news|release/.test(e.file_name||"")?"research":/policy/.test(e.file_name||"")?"claim":"report"}));
 const claims=selectedEvidence.map((e,i):JourneyItem=>({id:e.evidence_id!,label:topicName(e.packet||""),kind:"evidence",color:palette[i%5],artwork:topicArtwork(e.packet||"")}));
 const docEdges=selectedEvidence.map((e,i):JourneyEdge=>({id:"REF:"+e.evidence_id,source:docs[i].id,target:e.evidence_id!,flowType:"source_reference",relationshipStatus:"published_reference",tooltipText:"This published evidence record cites this source document.",presentation:true}));
 const methodSummaries=["Collect documents and preserve their identity.","Extract text, tables and recognized image text.","Keep each claim linked to its source passage.","Assess evidence strength and allowed interpretation.","Group ingredient, company, cost and logistics context.","Connect subjects through recorded relationships.","Prepare the published data for the website.","Explore the model and return to its sources."];
 const methodArtwork:StoryObjectName[]=["archive","scanner","database","audit","packets","graph","charts","website"];
 const methods=["Source vault","Level 1 parser","Evidence records","Level 2 audit","Structured packets","Node & edge builder","Display artifacts","Interactive website"].map((label,i):JourneyItem=>({id:"method-"+i,label,kind:"method",color:palette[i%5],core:false,tag:`Step ${i+1}`,summary:methodSummaries[i],artwork:methodArtwork[i]}));
 const methodEdges=methods.slice(1).map((m,i):JourneyEdge=>({id:"METHOD:"+i,source:methods[i].id,target:m.id,flowType:"workflow",relationshipStatus:"explanatory_sequence",tooltipText:"An explanatory stage in the original project workflow; not a live job.",presentation:true}));
 const chapter=(label:string,title:string,body:string,art:number,pattern:JourneyChapter["pattern"],items:JourneyItem[],edges=graphEdges):JourneyChapter=>{
  const selectedEdges=edges.filter(e=>items.some(n=>n.id===e.source)&&items.some(n=>n.id===e.target));
  if(kind==="method"){const total=items.length;const positioned=items.map((item,index)=>({...item,core:false,position:total>4?{x:index<4?12+index*25:87-(index-4)*25,y:index<4?24:72}:{x:15+index/Math.max(1,total-1)*70,y:48}}));return{label,title,body,art:-2,pattern,items:positioned,edges:selectedEdges};}
  if(pattern==="library"){
   const core:JourneyItem={id:"LIBRARY:"+kind,label:kind==="sources"?"Research archive":"Evidence library",kind:"method",color:"#a9d8ee",core:true};
   const memberEdges=items.filter(n=>n.kind==="evidence").map((n):JourneyEdge=>({id:"MEMBER:"+n.id,source:n.id,target:core.id,flowType:"collection_reference",relationshipStatus:"published_collection_member",tooltipText:"This evidence record belongs to the published collection.",presentation:true}));
   return{label,title,body,art:kind==="sources"?5:3,pattern,items:[core,...items],edges:[...selectedEdges,...memberEdges]};
  }
  return{label,title,body,art,pattern,items,edges:selectedEdges};
 };
 const costChapter=(label:string,title:string,body:string,items:JourneyItem[],art=4)=>{const center=node(product,0,true);if(center)center.label=art===4?"Cost layers":art===0?"Ingredient costs":art===1?"Making and delivery":"Retail comparison";const all=center?[center,...items]:items;const edges=center?items.map((n):JourneyEdge=>({id:"COSTREF:"+n.id,source:n.id,target:product,flowType:"cost_reference",relationshipStatus:"benchmark_only",tooltipText:"A recorded benchmark value for the product model; not a supplier invoice.",presentation:true})):[];return chapter(label,title,body,art,"layers",all,edges)};
 const supplyOverview=()=>{
  const retailers=(data?.graph.nodes||[]).filter(item=>item.type==="retailer"&&item.id);
  const positions:Array<[string,number,number]>=[["NODE_ORIGIN_COCOA",8,8],["NODE_ORIGIN_SUGAR",8,31],["NODE_ORIGIN_DAIRY",8,54],["NODE_ING_SOY_LECITHIN",8,77],["NODE_PACKAGING_STREAM",27,92],[receiving,36,45],["NODE_WAREHOUSE_DISTRIBUTION_CENTER",57,45],["NODE_DISTRIBUTOR_MCLANE",72,45],...retailers.map((item,index):[string,number,number]=>[item.id!,90,8+index*24])];
  const items=positions.map(([id,x,y],i)=>{const value=node(id,i,id===receiving);return value?{...value,label:id===receiving?"Manufacturing":value.label,position:{x,y}}:undefined}).filter((value):value is JourneyItem&{position:{x:number;y:number}}=>Boolean(value));
  const path=(start:string,end:string):string[]|null=>{const queue=[{id:start,edges:[] as string[]}],seen=new Set([start]);while(queue.length){const next=queue.shift()!;if(next.id===end)return next.edges;for(const edge of graphEdges.filter(edge=>edge.source===next.id)){if(seen.has(edge.target)||edge.flowType==="cost_reference")continue;seen.add(edge.target);queue.push({id:edge.target,edges:[...next.edges,edge.id]})}}return null};
  const pairs:Array<[string,string]>=[["NODE_ORIGIN_COCOA",receiving],["NODE_ORIGIN_SUGAR",receiving],["NODE_ORIGIN_DAIRY",receiving],["NODE_ING_SOY_LECITHIN",receiving],["NODE_PACKAGING_STREAM",receiving],[receiving,"NODE_WAREHOUSE_DISTRIBUTION_CENTER"],["NODE_WAREHOUSE_DISTRIBUTION_CENTER","NODE_DISTRIBUTOR_MCLANE"],...retailers.map((item):[string,string]=>["NODE_DISTRIBUTOR_MCLANE",item.id!])];
  const edges:JourneyEdge[]=pairs.flatMap(([source,target])=>{const sourceEdgeIds=path(source,target);if(!sourceEdgeIds)return[];const from=items.find(item=>item.id===source),to=items.find(item=>item.id===target);if(!from||!to)return[];return[{id:"SUPPLY_OVERVIEW:"+source+":"+target,source,target,sourceEdgeIds,presentation:true,flowType:"summarized_model_path",relationshipStatus:"modeled_context",materialFlow:from.label+" → "+to.label,tooltipText:"A simplified view of "+sourceEdgeIds.length+" connected steps in the published model. It does not establish exact supplier allocation or a tracked delivery route."}]});
  return chapter("Overview","From ingredients\nto the shelf.","Follow the ingredients into manufacturing, then explore storage, distribution and retail. Open a subject for its story, per-bar cost and supporting research.",1,"converge",items,edges);
 };
 if(kind==="home"||kind==="supply")return [
 kind==="supply"?supplyOverview():chapter("Overview","One bar.\nA whole supply chain.","Explore the product and the records connected to it. Scroll to follow the changing journey; select a subject or flowing connection for detail.",-1,"orbit",overview),
 chapter("Ingredient streams","Different origins.\nConnected inputs.","Sugar, cocoa and dairy streams pass through recorded company-level partner context. The raw-material node connects the branches.",0,"converge",upstream),
 chapter("Other inputs","Small ingredients.\nImportant roles.","Explore the minor ingredients and packaging in the model. Open each input to see what is recorded and what remains unknown.",0,"converge",minor),
 chapter("Manufacturing","Ingredients meet.\nChocolate takes shape.","Follow the modeled process through receiving, storage, processing, cooling and wrapping. Each connection comes from the published graph.",1,"process",process),
 chapter("Distribution","A finished bar.\nThe next journey.","The product moves through modeled warehouse, freight, distributor and retail relationships. Open a connection to inspect its scope.",2,"route",downstream),
 kind==="home"?chapter("Evidence","Open the research.\nUnderstand the story.","Source documents connect directly to the evidence records citing them. Continue below into the complete research and cost explorers.",3,"library",[...docs.slice(0,3),...claims.slice(0,3)],docEdges):costChapter("Cost layers","Cost travels\nwith the product.","Explore the existing allocation records. The complete per-bar model and all graph nodes remain available below.",[...costs,...retail])
 ];
 if(kind==="cost")return [
 costChapter("Composition","What goes\ninto the price?","The physical-cost categories connect to the product they describe. Select a layer for its recorded range and assumptions.",costs),
 costChapter("Ingredients","The recipe.\nIts cost assumptions.","Ingredient calculations contribute to the per-bar benchmark. The scenario explorer below retains the published low, base and high values.",ingredientCosts,0),
 costChapter("Making & delivery","Make it. Wrap it.\nMove it.","Packaging, conversion, storage and freight are separate recorded allocations, counted once in the physical cost total.",costs,1),
 costChapter("Retail comparison","Shelf price.\nA different measure.","Observed retail and the residual channel pool are separate measures. The residual is not a profit or margin claim.",retail,2)
 ];
 if(kind==="method")return [
 chapter("Overview","How research becomes\nan explorable world.","The original project moves from public documents to an explorable model. Follow the real sequence; open a stage for its role.",3,"process",methods,methodEdges),
 chapter("Extract","Read the documents.\nPreserve their context.","The source vault flows through parsing and extraction into source-attributed evidence records.",5,"route",methods.slice(0,3),methodEdges),
 chapter("Audit","Qualify the claim.\nKeep its limits.","Evidence enters the audit and becomes structured ingredient, supplier, cost and logistics context.",3,"process",methods.slice(2,5),methodEdges),
 chapter("Explore","Connect the records.\nMake them explorable.","The graph and cost model become published display artifacts. The interactive website keeps a path back to evidence.",4,"route",methods.slice(4),methodEdges)
 ];
 return [
 chapter("Overview",kind==="sources"?"Open the research\nbehind the model.":"Follow a claim\nto its source.","Each source is a unique document. Its connecting ribbons lead to the actual approved evidence records that cite it.",kind==="sources"?5:3,"library",[...docs.slice(0,3),...claims.slice(0,3)],docEdges),
 chapter("Choose a subject","Find the subject.\nFollow its context.","Explore the primary ingredient streams and their recorded partner context; use the complete filters below for any ingredient or source.",0,"converge",upstream),
 chapter("Read the source","Open a record.\nRead the context.","The document remains visible while its evidence opens beside it. Inspect the captured text, confidence and scope.",5,"library",[...docs.slice(1),...claims.slice(1)],docEdges),
 chapter("Interpret","Know what it supports.\nKnow where it ends.","Read the allowed interpretation alongside the source. The complete collection below is searchable by topic, source type and confidence.",3,"library",[...docs.slice(0,2),...claims.slice(0,2)],docEdges)
 ];
}
export function scenePosition(c:JourneyChapter,n:JourneyItem,i:number){
 if(n.position)return n.position;
 const total=c.items.length,core=c.items.find(x=>x.core);
 if(n.core)return c.pattern==="converge"?{x:82,y:50}:c.pattern==="route"?{x:10,y:48}:{x:50,y:50};
 const satellites=c.items.filter(x=>!x.core),j=satellites.findIndex(x=>x.id===n.id),t=j/Math.max(satellites.length,1);
 if(c.pattern==="converge"){
  if(n.id.includes("SUPPLIER")){const row=["ASR","BARRY","LAND"].findIndex(s=>n.id.includes(s));return{x:46,y:20+row*30};}
  return{x:12,y:15+(j-(c.items.slice(0,i).filter(x=>x.id.includes("SUPPLIER")).length))*Math.min(26,70/Math.max(satellites.filter(x=>!x.id.includes("SUPPLIER")).length-1,1))};
 }
 if(c.pattern==="route"&&n.kind==="node"){
  if(n.id.includes("WAREHOUSE"))return{x:30,y:48};
  if(n.id.includes("CARRIER"))return{x:48,y:48};
  if(n.id.includes("MCLANE"))return{x:65,y:48};
  if(n.id.includes("RETAILER"))return{x:82,y:13+["WALMART","TARGET","CVS","WALGREENS"].findIndex(s=>n.id.includes(s))*24};
  if(n.id==="NODE_CONSUMER")return{x:97,y:48};
 }
 if(c.pattern==="library")return n.kind==="source"?{x:22,y:18+c.items.filter(x=>x.kind==="source").findIndex(x=>x.id===n.id)*28}:{x:76,y:18+c.items.filter(x=>x.kind!=="source"&&!x.core).findIndex(x=>x.id===n.id)*28};
 if(c.pattern==="layers"){const rows=Math.ceil(satellites.length/2);return{x:j%2?84:16,y:rows===1?48:10+Math.floor(j/2)*80/Math.max(1,rows-1)};}
 if(c.pattern==="process"&&!core){return{x:12+(i%4)*25,y:25+Math.floor(i/4)*50}}
 if(c.pattern==="route")return{x:12+i/Math.max(total-1,1)*76,y:45+Math.sin(i/Math.max(total-1,1)*Math.PI)*15};
 const angle=t*Math.PI*2-Math.PI/2;
 return{x:50+Math.cos(angle)*38,y:50+Math.sin(angle)*37};
}
