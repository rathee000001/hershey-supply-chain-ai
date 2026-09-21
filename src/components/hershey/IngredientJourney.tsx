"use client";
import {useState} from "react";
import type {CostRecord} from "@/lib/hershey/enrichedArtifacts";
import StoryQuestions from "./StoryQuestions";
import SubjectIllustration from "./SubjectIllustration";
import {storyObjectFor} from "./StoryObject";
import {formatCents} from "./IngredientPanels";
export default function IngredientJourney({record,onCost,onSources}:{record:CostRecord;onCost:()=>void;onSources:()=>void}){
 const[step,setStep]=useState("origin");
 const art=storyObjectFor(record.model_ingredient_id||record.cost_bucket_id)||"minor";
 const story=record.ingredient_story;
 return <section className="he-answer">
 <StoryQuestions label="Follow this ingredient" value={step} onChange={setStep} items={[
 {id:"origin",label:"Where it starts",question:"What origin context is recorded?",hint:"Start with the ingredient, not an assumed supplier",art},
 {id:"preparation",label:"How it is prepared",question:"How does it move toward manufacturing?",hint:"Follow the saved processing description",art:"factory"},
 {id:"contribution",label:"Its place in the bar",question:"What contribution does the model assign?",hint:"Connect this input to the per-bar estimate",art:"coins"}]}/>
 <div className="panel-context-lead"><SubjectIllustration name={art} size={64}/><h3>{record.label}</h3></div>
 {step==="origin"?<p>{story?.origin||"No separate origin description is published for this input."}</p>:step==="preparation"?<><p>{story?.processing||"No separate processing description is published for this input."}</p>{story?.process_steps?.length?<ol className="ih-material-flow">{story.process_steps.map((label,index)=><li key={index}><span>{label}</span></li>)}</ol>:null}</>:<><div className="he-price-facts"><div><span>Base estimate per bar</span><strong>{formatCents(record.base_cents_per_bar)}</strong></div><div><span>Published range</span><strong>{formatCents(record.low_cents_per_bar)}–{formatCents(record.high_cents_per_bar)}</strong></div></div><p>{record.cost_logic}</p></>}
 <p className="he-boundary">This is the recorded ingredient model, not proof of a particular farm, exact supplier allocation or proprietary recipe.</p>
 <div className="story-mini-actions"><button onClick={onCost}>Inspect the calculation →</button><button onClick={onSources}>Read the supporting sources →</button></div>
 </section>;
}
