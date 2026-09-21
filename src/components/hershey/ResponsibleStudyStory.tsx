"use client";
import {useState} from "react";
import Link from "next/link";
import StoryQuestions from "./StoryQuestions";
export default function ResponsibleStudyStory(){
 const[view,setView]=useState("explore");
 return <div className="ih-inline-detail"><StoryQuestions label="Understand the study result" value={view} onChange={setView} items={[
 {id:"explore",label:"Explore the model",question:"What can you do with this study?",hint:"Connect subjects, estimates and sources",art:"graph"},
 {id:"check",label:"Check an explanation",question:"How can you examine a claim?",hint:"Keep interpretation and original separate",art:"report"},
 {id:"limits",label:"Know the limits",question:"What remains unproven?",hint:"Recognize where evidence ends",art:"audit"}]}/>
 {view==="explore"?<><p>Follow ingredients and company context, inspect the modeled production and delivery stages, compare cost assumptions, and open the underlying research.</p><p>A connection is a starting point for inspection. Open its subjects to see their roles, follow the calculation behind an estimate, or turn through the original source.</p><Link className="ih-inline-action" href="/supply-chain">Explore the supply chain →</Link></>:view==="check"?<><p>Read the study’s interpretation first, then compare it with the source pages. Check whether a statement concerns a product label, a company-wide relationship, a retailer observation or a model assumption.</p><p>The document reader preserves the original pages. Opening the research does not run a new AI analysis or make the underlying claim more certain.</p><Link className="ih-inline-action" href="/evidence-brain">Examine the evidence →</Link></>:<><p>The study does not establish:</p><ul><li>The exact supplier or route for an individual bar.</li><li>Hershey’s proprietary recipe or internal production costs.</li><li>Profit from the difference between a cost estimate and a shelf price.</li><li>Live prices or a live AI processing job.</li></ul><Link className="ih-inline-action" href="/cost-model">Inspect the cost assumptions →</Link></>}
 <p className="ih-fine">Independent academic project by Praveen Rathee.</p></div>;
}
