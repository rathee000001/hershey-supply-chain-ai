import catalog from "./generated/document-catalog.json";
const identities=new Map(catalog.documents.map(document=>[document.file_name,document.sha256]));
/** Preserve source aliases, but count identical original bytes as one document. */
export function documentIdentity(fileName:string){return identities.get(fileName)||fileName;}
