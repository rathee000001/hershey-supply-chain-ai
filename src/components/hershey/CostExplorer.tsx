"use client";
import {useState,type CSSProperties} from "react";
import {Bean,Package,Factory,Warehouse,Truck,ShoppingBag,ShieldCheck,ArrowDown} from "lucide-react";
import type {EnrichedArtifacts,CostRecord} from "@/lib/hershey/enrichedArtifacts";
import {HersheyOrb as Orb} from "./HersheyOrb";
import IngredientPanels,{CalculationPanel,formatCents,type FamilyName} from "./IngredientPanels";
import "./cost-explorer.css";
import StoryQuestions from "./StoryQuestions";
import {SubjectGlass,type StoryObjectName} from "./StoryObject";
const layerObjects:Record<string,StoryObjectName>={ingredient:"cocoa",packaging:"packaging",manufacturing_conversion:"factory",storage:"warehouse",freight:"truck"};
type Scenario="low"|"base"|"high";
const layers=[
 {id:"ingredient",name:"Ingredients",hint:"Cocoa, sugar, dairy and smaller inputs",Icon:Bean,color:"#ddaa79",family:"cocoa"},
 {id:"packaging",name:"Packaging",hint:"Wrapper and packaging allocation",Icon:Package,color:"#b9d9fa",family:"packaging"},
 {id:"manufacturing_conversion",name:"Making the bar",hint:"The manufacturing conversion estimate",Icon:Factory,color:"#efc26f",family:"manufacturing"},
 {id:"storage",name:"Warehousing",hint:"The storage and handling estimate",Icon:Warehouse,color:"#84d1ec",family:"logistics"},
 {id:"freight",name:"Freight",hint:"The outbound transport estimate",Icon:Truck,color:"#c5a4ec",family:"logistics"},
] as const;
export default function CostExplorer({data,scenario,setScenario,view="all",selectedLayer,onLayerChange}:{data:EnrichedArtifacts;scenario:Scenario;setScenario:(value:Scenario)=>void;view?:"all"|"layers"|"detail"|"comparison";selectedLayer?:string;onLayerChange?:(value:string)=>void}){
 const[comparisonTab,setComparisonTab]=useState<"gap"|"retail">("gap");
 const[localSelected,setLocalSelected]=useState<string>("ingredient");const selected=selectedLayer||localSelected,setSelected=onLayerChange||setLocalSelected;
 const key=(scenario+"_cents_per_bar") as "base_cents_per_bar",records=(data.costBreakdown.records||[]).filter(r=>r.safe_display===true);
 const sums=layers.map(layer=>({...layer,records:records.filter(r=>r.cost_type===layer.id),value:records.filter(r=>r.cost_type===layer.id).reduce((sum,r)=>sum+r[key],0)}));
 const active=sums.find(layer=>layer.id===selected)!,physical=data.costBreakdown.physical_cost?.[key],retail=data.costBreakdown.retail_price?.[key],residual=data.costBreakdown.residual_channel_pool?.[key];
 const reference=retail&&retail>0?retail:1;
 const gapRetail=scenario==="high"?data.costBreakdown.retail_price?.high_cents_per_bar:scenario==="low"?data.costBreakdown.retail_price?.low_cents_per_bar:data.costBreakdown.retail_price?.base_cents_per_bar;
 const gapPhysical=scenario==="high"?data.costBreakdown.physical_cost?.low_cents_per_bar:scenario==="low"?data.costBreakdown.physical_cost?.high_cents_per_bar:data.costBreakdown.physical_cost?.base_cents_per_bar;
 return <div className="ce-explorer" data-cost-view={view} data-comparison-tab={comparisonTab}><p className="hc-eyebrow">THE PER-BAR COST STORY</p><h2>Choose a layer. See what contributes.</h2><p>The figures below all use cents per bar. Ingredient quantities and benchmark prices are estimates—not Hershey's internal costs.</p>
 <div className="ce-scenarios" role="group" aria-label="Cost estimate scenario">{(["low","base","high"] as const).map(value=><button key={value} aria-pressed={scenario===value} onClick={()=>setScenario(value)}><strong>{value[0].toUpperCase()+value.slice(1)}</strong><span>{value==="base"?"Central estimate":value==="low"?"Lower estimate":"Upper estimate"}</span></button>)}</div>
 {view==="comparison"&&<StoryQuestions label="Retail comparison details" value={comparisonTab} onChange={value=>setComparisonTab(value as "gap"|"retail")} items={[
{id:"gap",label:"Understand the gap",question:"Why is shelf price different from estimated cost?",hint:"Compare distinct measures without calling the gap profit",art:"charts"},
{id:"retail",label:"Retailer observations",question:"What prices did the research record?",hint:"Compare the four saved observations",art:"retail"}]}/>}
 <div className="ce-overview"><div className="ce-layers">{sums.map(layer=><button key={layer.id} aria-pressed={selected===layer.id} onClick={()=>setSelected(layer.id)} style={{"--cost-tone":layer.color} as CSSProperties}><SubjectGlass name={layerObjects[layer.id]}/><div><h3>{layer.name}</h3><p>{layer.hint}</p></div><strong>{formatCents(layer.value)}</strong><ArrowDown size={17}/></button>)}</div>
 <section className="ce-comparison" aria-label="Physical cost and observed shelf price"><h3>Cost and shelf price are different measures.</h3><div className="ce-columns"><div className="ce-column"><strong>{physical!=null?formatCents(physical):"Not available"}</strong><div className="ce-column-track"><div className="ce-physical-column" style={{height:Math.max(0,Math.min(100,(physical||0)/reference*100))+"%"}}>{[...sums].reverse().map(layer=><span key={layer.id} title={layer.name+": "+formatCents(layer.value)} style={{height:(physical?layer.value/physical*100:0)+"%",background:layer.color}}/>)}</div></div><span>Estimated physical cost</span></div><div className="ce-column"><strong>{retail!=null?formatCents(retail):"Not available"}</strong><div className="ce-column-track"><div className="ce-retail-column"/></div><span>{scenario==="base"?"Average observed shelf price":scenario==="low"?"Lowest observed shelf price":"Highest observed shelf price"}</span></div></div><p>Column heights use the same cents-per-bar scale. Retail observations are separate from the cost assumptions.</p></section></div>
 <section className="ce-layer-detail" style={{"--cost-tone":active.color} as CSSProperties}><div className="ce-detail-heading"><SubjectGlass name={layerObjects[active.id]}/><div><p className="hc-eyebrow">EXPLORE THIS LAYER</p><h2>{active.name}</h2></div></div>
 {selected==="ingredient"?<IngredientPanels data={data} initialFamily="cocoa" families={["sugar","cocoa","dairy","minor"]} scenario={scenario} onScenarioChange={setScenario}/>:active.records.length?active.records.map(record=><CalculationPanel key={record.cost_bucket_id} record={record} data={data} scenario={scenario}/>):<p>No separate calculation is published for this layer.</p>}
 </section>
 <section className="ce-gap"><ShieldCheck size={29}/><div><h2>The remaining gap is not profit.</h2><p>It can include channel margins, promotions, taxes or fees, overhead and estimation error. The study does not determine how that gap is divided.</p><strong>{residual!=null?formatCents(residual):"Not available"}</strong><span>{scenario==="base"?"Base channel / commercial gap":scenario==="low"?"Lower published gap bound":"Upper published gap bound"}</span><p className="ce-gap-formula">{gapRetail!=null&&gapPhysical!=null?formatCents(gapRetail)+" observed price − "+formatCents(gapPhysical)+" physical estimate":"Comparison inputs not available"}</p><p>{scenario==="base"?"The base gap compares the average observed shelf price with the base physical-cost estimate.":scenario==="low"?"The lower gap bound pairs the lowest observed shelf price with the highest physical-cost estimate. It is not the difference between the two Low columns above.":"The upper gap bound pairs the highest observed shelf price with the lowest physical-cost estimate. It is not the difference between the two High columns above."}</p></div></section>
 <section className="ce-retail"><p className="hc-eyebrow">THE RETAIL OBSERVATIONS</p><h2>What the research actually recorded.</h2><div className="ce-retailer-cards">{data.calculationDetails.verified_retailers.map(item=><div key={item.retailer}><SubjectGlass name="retail"/><h3>{item.retailer.toLowerCase()==="cvs"?"CVS":item.retailer[0].toUpperCase()+item.retailer.slice(1)}</h3><strong>{formatCents(item.price_cents_per_bar)}</strong><span>observed single-bar price</span><small>{item.observation_date||"Observation date not captured"}</small></div>)}</div><p>These are saved observations, not live price quotes. Store, date and promotion can change the amount.</p></section>
 </div>;
}
