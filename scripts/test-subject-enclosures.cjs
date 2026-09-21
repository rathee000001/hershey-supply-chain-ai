const assert=require('node:assert/strict');
const fs=require('node:fs');
const ts=require('typescript');
const sharp=require('sharp');
const exportsObject={};
new Function('exports',ts.transpileModule(fs.readFileSync('src/components/hershey/fit-subject-bounds.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText)(exportsObject);
(async()=>{
 const {data,info}=await sharp('public/home-art/home-subjects-v2.png').ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const cw=info.width/3,ch=info.height/3;
 for(const cell of [0,1,2,4,5,6,7]){
  const x0=cell%3*cw,y0=Math.floor(cell/3)*ch;
  const fit=exportsObject.fitSubjectBounds(data,info.width,x0,y0,cw,ch,1.65,1.65);
  assert(Object.values(fit).every(Number.isFinite),'non-finite fit');
  let visible=0;
  for(let y=0;y<ch;y++)for(let x=0;x<cw;x++){
   if(data[((y0+y)*info.width+x0+x)*4+3]<32)continue;
   visible++;
   const px=((x+.5)/cw-.5)*1.65,py=(.5-(y+.5)/ch)*1.65;
   assert(Math.hypot((px-fit.centerX)/fit.radiusX,(py-fit.centerY)/fit.radiusY)<1,`subject outside enclosure: cell ${cell}`);
  }
  assert(visible>0);console.log(`PASS cell ${cell}: ${visible} visible pixels enclosed; radii ${fit.radiusX.toFixed(3)} x ${fit.radiusY.toFixed(3)}`);
 }
})().catch(error=>{console.error(error);process.exitCode=1});
