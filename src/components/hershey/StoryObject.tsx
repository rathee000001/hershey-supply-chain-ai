import {useId} from "react";
import Image from "next/image";
import HomeSubjectArtwork from "./HomeSubjectArtwork";
export type StoryObjectName="product"|"warehouse"|"retail"|"people"|"soy"|"packaging"|"minor"|"report"|"research"|"claim"|"cocoa"|"sugar"|"dairy"|"factory"|"truck"|"coins"|"archive"|"scanner"|"database"|"audit"|"packets"|"graph"|"charts"|"website";
const workflow:Partial<Record<StoryObjectName,number>>={archive:0,scanner:1,database:2,audit:3,packets:4,graph:5,charts:6,website:7};
const crops:Partial<Record<StoryObjectName,[number,number,number,number]>>={warehouse:[9,92,400,331],retail:[427,62,435,359],people:[910,21,260,431],soy:[26,496,393,294],packaging:[444,489,397,313],minor:[875,499,336,306],report:[2,891,438,324],research:[450,849,416,352],claim:[907,837,304,375]};
const workflowCrops:Array<[number,number,number,number]>=[[49,27,377,398],[468,55,410,330],[966,55,279,334],[1365,17,379,406],[30,460,407,384],[484,461,357,345],[927,453,372,387],[1340,474,404,352]];
const home:Partial<Record<StoryObjectName,0|1|2|4|5|7>>={cocoa:0,sugar:1,dairy:2,factory:4,truck:5,coins:7};
export function storyObjectFor(id:string,kind?:string):StoryObjectName|undefined{
 if(id==="NODE_PRODUCT_HERSHEY_155OZ")return"product";
 if(kind==="source")return"report";if(kind==="evidence")return"claim";
 if(/COCOA|CHOCOLATE/.test(id))return"cocoa";if(/SUGAR/.test(id))return"sugar";if(/DAIRY|MILK/.test(id))return"dairy";
 if(/SOY/.test(id))return"soy";if(/PGPR|FLAVOR/.test(id))return"minor";if(/PACKAGING|WRAPPING/.test(id))return"packaging";
 if(/WAREHOUSE|STORAGE/.test(id))return"warehouse";if(/CARRIER|FREIGHT/.test(id))return"truck";if(/RETAILER/.test(id))return"retail";if(/CONSUMER/.test(id))return"people";
 if(/PROCESS_RECEIVING/.test(id))return"packaging";if(/PROCESS|MANUFACTURING/.test(id))return"factory";
 return undefined;
}
export default function StoryObject({name}:{name:StoryObjectName}){
 const clipId=useId().replace(/:/g,"");
 if(name==="product")return <Image className="story-object" src="/home-art/product.png" alt="" aria-hidden="true" width={1200} height={800} unoptimized style={{objectFit:"contain"}}/>;
 const cell=home[name];if(cell!==undefined)return <HomeSubjectArtwork cell={cell}/>;
 const stage=workflow[name],isWorkflow=stage!==undefined,[x,y,w,h]=isWorkflow?workflowCrops[stage]:crops[name]!;
 return <svg aria-hidden="true" className={"story-object"+(isWorkflow?" workflow-object":"")} viewBox={`${x} ${y} ${w} ${h}`} preserveAspectRatio="xMidYMid meet" data-artwork={name}><defs><clipPath id={clipId}><rect x={x} y={y} width={w} height={h}/></clipPath></defs><image href={isWorkflow?"/home-art/workflow-objects-v1.png":"/home-art/story-objects-v1.png"} width={isWorkflow?1774:1230} height={isWorkflow?887:1278} clipPath={`url(#${clipId})`}/></svg>;
}
export function SubjectGlass({name}:{name:StoryObjectName}){return <span className="subject-glass" data-object={name}><StoryObject name={name}/></span>;}
