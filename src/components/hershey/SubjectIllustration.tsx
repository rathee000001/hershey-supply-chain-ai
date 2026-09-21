import StoryObject,{type StoryObjectName} from "./StoryObject";
/** Existing subject artwork, sized for headings and cards without a second shell. */
export default function SubjectIllustration({name,size=48}:{name:StoryObjectName;size?:number}){
 return <span className="panel-subject-illustration" data-subject-art={name} aria-hidden="true" style={{width:size,height:size,flexBasis:size}}><StoryObject name={name}/></span>;
}
