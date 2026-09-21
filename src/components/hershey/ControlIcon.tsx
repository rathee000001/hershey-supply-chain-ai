"use client";
import type {ReactNode} from "react";
export type ControlIconName="home"|"supply"|"evidence"|"cost"|"sources"|"how";
// Home, document and play geometry follows the MIT-licensed reference navigation.
// Hershey-specific meanings stay separate from the reference site's branded subjects.
const shapes:Record<ControlIconName,ReactNode>={
 home:<><path d="m3 10 9-7 9 7M5 9v12h14V9"/><path d="M9 21v-7h6v7"/></>,
 supply:<><rect x="8.5" y="2" width="7" height="6" rx="1"/><path d="M12 8v5M5 13h14M5 13v3m14-3v3"/><rect x="1.5" y="16" width="7" height="6" rx="1"/><rect x="15.5" y="16" width="7" height="6" rx="1"/></>,
 evidence:<><path d="M5 2h9l5 5v7M5 2v19h8M14 2v6h5"/><circle cx="14" cy="15" r="4"/><path d="m17 18 4 4M8 11h2"/></>,
 cost:<><ellipse cx="9" cy="15" rx="6" ry="7"/><path d="M9 11v8m2-7H8a1.5 1.5 0 0 0 0 3h2a1.5 1.5 0 0 1 0 3H7"/><path d="M12 3a6 7 0 1 1 5 13M17 4v7"/></>,
 sources:<><path d="M3 4h5a5 5 0 0 1 4 2 5 5 0 0 1 4-2h5v15h-5a5 5 0 0 0-4 2 5 5 0 0 0-4-2H3V4ZM12 6v15"/><path d="M6 8h3m6 0h3M6 12h3m6 0h3"/></>,
 how:<><circle cx="12" cy="12" r="9"/><path d="m10 7 7 5-7 5Z"/></>
};
export default function ControlIcon({name}:{name:ControlIconName}){return <svg data-nav-icon={name} viewBox="0 0 26 26" width="26" height="26" aria-hidden="true" fill="none" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><g transform="translate(1 1)"><g transform="translate(.7 1)" stroke="#020c1c" strokeWidth="2.4">{shapes[name]}</g><g stroke="var(--glass-orb-color,#a5eaff)">{shapes[name]}</g></g></svg>}
