import type {JourneyChapter,JourneyItem,JourneyEdge} from "./scene-model";
const topics:Record<string,JourneyItem>={
 product:{id:"HOME:product",label:"The chocolate bar",kind:"method",color:"#b3ceff",core:true},
 ingredients:{id:"HOME:ingredients",label:"Ingredients",kind:"method",color:"#8adfc0"},
 manufacturing:{id:"HOME:manufacturing",label:"Manufacturing",kind:"method",color:"#b9adff"},
 distribution:{id:"HOME:distribution",label:"Distribution",kind:"method",color:"#8edbff"},
 evidence:{id:"HOME:evidence",label:"Evidence",kind:"method",color:"#c6a2ff"},
 cost:{id:"HOME:cost",label:"Cost",kind:"method",color:"#f1c879"},
 sugar:{id:"HOME:sugar",label:"Sugar",kind:"method",color:"#ece0b3"},
 dairy:{id:"HOME:dairy",label:"Milk & dairy",kind:"method",color:"#a8e1ff"},
 retail:{id:"HOME:retail",label:"Retail",kind:"method",color:"#edb78e"},
 people:{id:"HOME:people",label:"People",kind:"method",color:"#8edbff"},
 minor:{id:"HOME:minor",label:"Other ingredients",kind:"method",color:"#d4b4ff"},
 study:{id:"HOME:study",label:"About this study",kind:"method",color:"#b9caff"},
};
type Position=[string,number,number];
function chapter(label:string,title:string,body:string,art:number,positions:Position[],core:string,links:Array<[string,string]>):JourneyChapter{
 const items=positions.map(([name,x,y])=>({...topics[name],core:name===core,position:{x,y}}));
 const edges:JourneyEdge[]=links.map(([a,b])=>({id:"HOME_STORY:"+label+":"+a+":"+b,source:topics[a].id,target:topics[b].id,materialFlow:topics[a].label+" → "+topics[b].label,flowType:"story_navigation",relationshipStatus:"illustrative_workflow",presentation:true,tooltipText:label+": explore "+topics[a].label.toLowerCase()+" and its connection to "+topics[b].label.toLowerCase()+". This is a guided explanation; open either subject for its recorded evidence and calculation limits."}));
 return{label,title,body,art,pattern:"orbit",items,edges};
}
export const approvedHomeStory=[
 chapter("Overview","One bar.\nA whole supply chain.","Follow the journey of a milk chocolate bar—from its ingredients to the shelf. Explore the public research and calculated costs behind the story.",-1,[["product",52,51],["ingredients",18,16],["manufacturing",57,7],["distribution",89,31],["evidence",13,79],["cost",70,87]],"product",[["ingredients","manufacturing"],["manufacturing","distribution"],["distribution","cost"],["cost","evidence"],["evidence","ingredients"]]),
 chapter("Ingredient origins","Different ingredients.\nOne chocolate bar.","Open cocoa, sugar, dairy or the smaller ingredients. Follow the source context, modeled quantities and cost calculations behind each group.",0,[["ingredients",17,18],["sugar",15,76],["dairy",85,20],["minor",84,78],["product",51,48]],"product",[["ingredients","product"],["sugar","product"],["dairy","product"],["minor","product"]]),
 chapter("From factory to shop shelf","From the factory.\nTo the people.","Follow manufacturing, distribution and retail. Each step opens its own process, logistics or price records, with modeled relationships clearly distinguished from observations.",1,[["manufacturing",15,38],["distribution",40,38],["retail",65,38],["people",88,38],["cost",53,82]],"none",[["manufacturing","distribution"],["distribution","retail"],["retail","people"],["manufacturing","cost"],["retail","cost"]]),
 chapter("About this study","A real product.\nA transparent study.","Explore the product scope, academic context and public sources behind this independent study. Inspect the evidence and calculations without mistaking estimates for company disclosures.",3,[["product",52,48],["study",18,26],["evidence",83,25],["cost",83,80]],"product",[["study","product"],["product","evidence"],["product","cost"]])
];
