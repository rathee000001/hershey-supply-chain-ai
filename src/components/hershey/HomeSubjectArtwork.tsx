import type {CSSProperties} from "react";
/** Dedicated Home subject atlas; unused decorative food cell is deliberately excluded. */
export default function HomeSubjectArtwork({cell,className=""}:{cell:0|1|2|4|5|6|7|8;className?:string}){return <span className={"ih-subject-art "+className} style={{"--home-art-x":(cell%3)*50+"%","--home-art-y":Math.floor(cell/3)*50+"%"} as CSSProperties} aria-hidden="true"/>;}
