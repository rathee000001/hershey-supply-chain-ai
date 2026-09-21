import type * as Three from "three";
import {fitSubjectBounds,type SubjectEnvelope} from "./fit-subject-bounds";

/** Existing authored subjects, retained in one live scene with coded shells and routes. */
export function createHomeGeometry(T:typeof Three){
 let disposed=false;
 const envelopes:Record<string,SubjectEnvelope>={};
 const subjectMeshes:Record<string,Three.Mesh>={};
 const geometries:Three.BufferGeometry[]=[],materials:Three.Material[]=[],textures:Three.Texture[]=[];
 const geo=<G extends Three.BufferGeometry>(g:G)=>{geometries.push(g);return g};
 const mat=<M extends Three.Material>(m:M)=>{materials.push(m);return m};
 const standard=(color:number,roughness=.45,metalness=.05)=>mat(new T.MeshPhysicalMaterial({color,roughness,metalness,clearcoat:.3}));
 const brown=standard(0x542713,.34),wrapper=standard(0x310b17,.27,.26),silver=standard(0xd6deea,.18,1),gold=standard(0xc99839,.22,.85),white=standard(0xe1dfd5,.38),dark=standard(0x131823,.7),green=standard(0x356b22,.45);
 const mesh=(geometry:Three.BufferGeometry,material:Three.Material|Three.Material[],parent:Three.Group,x=0,y=0,z=0)=>{const m=new T.Mesh(geometry,material);m.position.set(x,y,z);parent.add(m);return m};
 function label(text:string,bg:string,fg:string,w=1024,h=256){
  const canvas=document.createElement("canvas");canvas.width=w;canvas.height=h;const ctx=canvas.getContext("2d")!;ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);ctx.fillStyle=fg;ctx.textAlign="center";ctx.textBaseline="middle";ctx.font="900 "+Math.floor(h*.57)+"px Arial";ctx.fillText(text,w/2,h/2,w*.92);const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;textures.push(texture);return texture;
 }
 function rounded(w:number,h:number,d:number,r=.05){
  const s=new T.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);
  return geo(new T.ExtrudeGeometry(s,{depth:d,bevelEnabled:true,bevelSize:r*.6,bevelThickness:r*.6,bevelSegments:3,curveSegments:8,steps:1}));
 }
 const groups:Record<string,Three.Group>={};const group=(id:string)=>{const g=new T.Group();groups[id]=g;return g};
 const bar=group("HOME:product");
 mesh(rounded(5.6,2.45,.16,.08),brown,bar,0,0,-.08);
 const stamp=mat(new T.MeshStandardMaterial({map:label("HERSHEY’S","#602e19","#32160d"),roughness:.45}));
 const caps=geo(new T.PlaneGeometry(1.10,.34));
 for(let row=0;row<3;row++)for(let col=0;col<4;col++){const x=-2.10+col*1.40,y=-.78+row*.78;mesh(rounded(1.25,.65,.12,.055),brown,bar,x,y,.11);mesh(caps,stamp,bar,x,y,.258);}
 const coverMap=label("HERSHEY’S","#310c17","#fff1e5",1536,768);
 const coverCanvas=coverMap.image as HTMLCanvasElement,ctx=coverCanvas.getContext("2d")!;ctx.fillStyle="#f2e1da";ctx.font="600 52px Arial";ctx.textAlign="center";ctx.fillText("MILK CHOCOLATE",768,625);coverMap.needsUpdate=true;
 const coverFace=mat(new T.MeshPhysicalMaterial({map:coverMap,roughness:.28,metalness:.18,clearcoat:1,clearcoatRoughness:.18}));
 const covered=mesh(geo(new T.BoxGeometry(3.25,2.5,.42)),[wrapper,wrapper,wrapper,wrapper,coverFace,wrapper],bar,-1.18,0,.10);covered.rotation.z=.012;
 const foilGeo=geo(new T.PlaneGeometry(.76,2.65,16,40));const attr=foilGeo.attributes.position,rest=new Float32Array(attr.array.length);
 for(let i=0;i<attr.count;i++){const x=attr.getX(i),y=attr.getY(i),z=.09*Math.sin(y*31+x*18)+.055*Math.cos(x*47-y*19);attr.setXYZ(i,x+.075*Math.sin(y*21),y,z);rest.set([attr.getX(i),y,z],i*3)}foilGeo.computeVertexNormals();
 const foil=mesh(foilGeo,mat(new T.MeshPhysicalMaterial({color:0xe4e7eb,metalness:1,roughness:.19,side:T.DoubleSide,clearcoat:.7})),bar,.57,0,.38);foil.rotation.y=-.20;
 const fragments:Three.Mesh[]=[];for(let i=0;i<5;i++){const m=mesh(geo(new T.IcosahedronGeometry(.10+i*.017,0)),brown,bar,2.5+Math.sin(i*1.7)*.6,(i-2)*.68,.15+Math.cos(i)*.2);m.rotation.set(i*.7,i*.2,i);fragments.push(m)}
 bar.rotation.set(.12,-.14,-.23);

 const cocoa=group("HOME:ingredients");
 const pod=mesh(geo(new T.SphereGeometry(.35,32,24)),standard(0x84371f,.47),cocoa);pod.scale.set(1,1.75,.8);pod.rotation.z=-.4;
 for(let i=0;i<8;i++){const points=[];for(let j=0;j<=25;j++){const t=j/25*Math.PI;points.push(new T.Vector3(Math.sin(t)*.36*Math.cos(i*Math.PI/4),Math.cos(t)*.61,Math.sin(t)*.29*Math.sin(i*Math.PI/4)))}const rib=mesh(geo(new T.TubeGeometry(new T.CatmullRomCurve3(points),25,.013,5,false)),standard(0xc27a37,.5),cocoa);rib.rotation.z=-.4;}
 for(let i=0;i<3;i++){const leaf=mesh(geo(new T.SphereGeometry(.3,20,12)),green,cocoa,-.2+i*.2,.42+i*.06,-.08);leaf.scale.set(.55,1.6,.08);leaf.rotation.z=-.6+i*.55;}
 const sugar=group("HOME:sugar");
 const bowlProfile=[new T.Vector2(0,-.36),new T.Vector2(.18,-.36),new T.Vector2(.29,-.25),new T.Vector2(.39,-.07),new T.Vector2(.40,.01),new T.Vector2(.37,.025),new T.Vector2(.35,-.06),new T.Vector2(.22,-.22),new T.Vector2(0,-.24)];
 mesh(geo(new T.LatheGeometry(bowlProfile,48)),standard(0x673720,.48),sugar);
 const sugarHeap=mesh(geo(new T.SphereGeometry(.34,32,20)),standard(0xfff8e9,.78),sugar,0,.005,0);sugarHeap.scale.y=.38;
 const grains=new T.InstancedMesh(geo(new T.IcosahedronGeometry(.019,0)),white,120),grainPose=new T.Object3D();
 for(let i=0;i<120;i++){const angle=i*2.39996,radius=.33*Math.sqrt((i+.5)/120);grainPose.position.set(Math.cos(angle)*radius,.018+Math.sqrt(Math.max(0,.34*.34-radius*radius))*.38,Math.sin(angle)*radius);grainPose.rotation.set(i*.21,i*.13,i*.7);grainPose.updateMatrix();grains.setMatrixAt(i,grainPose.matrix)}sugar.add(grains);sugar.rotation.x=.2;
 const dairy=group("HOME:dairy");
 const glass=mat(new T.MeshPhysicalMaterial({color:0xd9f4ff,roughness:.06,metalness:.02,transmission:.85,thickness:.07,ior:1.46,transparent:true,opacity:.72,clearcoat:1,side:T.DoubleSide,depthWrite:false}));
 const pitcherProfile=[new T.Vector2(0,-.43),new T.Vector2(.23,-.43),new T.Vector2(.29,-.34),new T.Vector2(.28,.14),new T.Vector2(.19,.35),new T.Vector2(.19,.47),new T.Vector2(.215,.49)];
 mesh(geo(new T.LatheGeometry(pitcherProfile,64)),glass,dairy);
 const milkProfile=[new T.Vector2(0,-.40),new T.Vector2(.215,-.40),new T.Vector2(.265,-.32),new T.Vector2(.255,.12),new T.Vector2(0,.12)];
 mesh(geo(new T.LatheGeometry(milkProfile,48)),standard(0xfff9e8,.24),dairy);
 const handleCurve=new T.CatmullRomCurve3([new T.Vector3(.20,.33,0),new T.Vector3(.43,.28,0),new T.Vector3(.46,.04,0),new T.Vector3(.37,-.17,0),new T.Vector3(.27,-.20,0)]);
 mesh(geo(new T.TubeGeometry(handleCurve,40,.034,12,false)),glass,dairy);
 mesh(geo(new T.TorusGeometry(.206,.018,12,48)),glass,dairy,0,.475,0).rotation.x=Math.PI/2;

 const people=group("HOME:people"),personMaterial=standard(0x5ccde8,.22,.28);
 for(const[x,y,s]of [[-.37,-.04,.8],[0,.08,1],[.37,-.04,.8]]){const person=new T.Group();people.add(person);person.position.set(x,y,0);person.scale.setScalar(s);mesh(geo(new T.SphereGeometry(.14,28,20)),personMaterial,person,0,.29,.06);const shoulders=mesh(geo(new T.CapsuleGeometry(.16,.19,8,20)),personMaterial,person,0,-.09,0);shoulders.scale.set(1.18,1,.65);}

 const factory=group("HOME:manufacturing");
 const brick=standard(0xb1926d,.7),windowMat=mat(new T.MeshStandardMaterial({color:0xffd896,emissive:0xc28534,emissiveIntensity:.65}));
 mesh(geo(new T.BoxGeometry(1.1,.55,.65)),brick,factory,0,-.1,0);mesh(geo(new T.BoxGeometry(.75,.25,.53)),brick,factory,-.12,.3,-.06);
 for(let i=0;i<3;i++){mesh(geo(new T.CylinderGeometry(.047,.058,.65+i*.1,16)),silver,factory,-.35+i*.28,.65,-.09);for(let j=0;j<3;j++)mesh(geo(new T.BoxGeometry(.12,.12,.012)),windowMat,factory,-.36+j*.34,-.02-i*.11,.331);}
 const factorySign=mat(new T.MeshStandardMaterial({map:label("HERSHEY’S","#442621","#f4e6cf"),roughness:.7}));mesh(geo(new T.PlaneGeometry(.8,.20)),factorySign,factory,0,.12,.342);
 const smoke=Array.from({length:15},(_,i)=>{const m=mesh(geo(new T.SphereGeometry(.045,10,8)),mat(new T.MeshBasicMaterial({color:0xb6b1b2,transparent:true,opacity:.14,depthWrite:false})),factory,0,1,0);return m});

 const distribution=group("HOME:distribution"),wheels:Three.Mesh[]=[];
 const rig=new T.Group();distribution.add(rig);rig.rotation.set(.09,-.34,0);rig.scale.setScalar(.9);
 const truckPaint=standard(0x513566,.19,.4),truckGlass=standard(0x27465b,.09,.65),alloy=standard(0xa5b9ce,.2,.9);
 mesh(rounded(.85,.48,.40,.026),standard(0xcbd4e2,.32,.4),rig,.18,.11,-.21);
 mesh(rounded(.36,.43,.36,.045),truckPaint,rig,-.48,.055,-.19);
 mesh(rounded(.16,.20,.36,.018),truckPaint,rig,-.71,-.06,-.19);
 mesh(geo(new T.BoxGeometry(1.45,.055,.39)),dark,rig,-.05,-.18,0);
 mesh(geo(new T.BoxGeometry(.23,.16,.014)),truckGlass,rig,-.49,.15,.211);
 mesh(geo(new T.BoxGeometry(.23,.018,.014)),alloy,rig,-.49,.058,.225);
 mesh(geo(new T.BoxGeometry(.17,.085,.018)),alloy,rig,-.72,-.065,.215);
 for(let i=0;i<13;i++)mesh(geo(new T.BoxGeometry(.013,.43,.016)),alloy,rig,-.19+i*.061,.11,.207);
 for(const x of [-.53,.22,.46])for(const z of [-.255,.255]){const wheel=mesh(geo(new T.CylinderGeometry(.11,.11,.065,28)),dark,rig,x,-.20,z);wheel.rotation.x=Math.PI/2;wheels.push(wheel);const hub=mesh(geo(new T.CylinderGeometry(.052,.052,.07,20)),alloy,rig,x,-.20,z);hub.rotation.x=Math.PI/2;}
 for(const x of [-.77,-.66])mesh(geo(new T.BoxGeometry(.05,.035,.022)),windowMat,rig,x,-.065,.228);
 const retail=group("HOME:retail"),shop=new T.Group();retail.add(shop);shop.rotation.set(.08,-.25,0);
 const storeWall=standard(0xd4c5ad,.61),canopy=standard(0x267d9b,.29,.17),storeGlass=mat(new T.MeshPhysicalMaterial({color:0x71b7cf,roughness:.11,metalness:.25,transparent:true,opacity:.65,clearcoat:1}));
 mesh(rounded(.95,.68,.36,.018),storeWall,shop,0,-.03,-.20);
 mesh(geo(new T.BoxGeometry(1.03,.075,.5)),dark,shop,0,.34,0);
 mesh(geo(new T.BoxGeometry(.25,.47,.025)),storeGlass,shop,-.25,-.10,.19);
 mesh(geo(new T.BoxGeometry(.43,.34,.025)),storeGlass,shop,.18,-.04,.19);
 mesh(geo(new T.BoxGeometry(.018,.47,.045)),alloy,shop,-.10,-.10,.21);
 mesh(geo(new T.BoxGeometry(.03,.075,.03)),gold,shop,-.17,-.10,.23);
 for(let i=0;i<12;i++){const stripe=mesh(geo(new T.BoxGeometry(.082,.095,.25)),i%2?white:canopy,shop,-.45+i*.082,.25,.23);stripe.rotation.x=-.25;}
 mesh(geo(new T.PlaneGeometry(.59,.12)),mat(new T.MeshBasicMaterial({map:label("SHOP","#143644","#d8f5ff"),toneMapped:false})),shop,0,.42,.07);
 mesh(geo(new T.BoxGeometry(1.03,.07,.53)),standard(0x405768,.4),shop,0,-.405,0);

 const evidence=group("HOME:evidence"),paper=standard(0xdbecf5,.44,.12);
 for(let i=0;i<3;i++){const page=new T.Group();evidence.add(page);page.position.set((i-1)*.18,(i-1)*.08,-i*.05);page.rotation.z=(i-1)*.15;mesh(geo(new T.BoxGeometry(.52,.72,.018)),paper,page);for(let j=0;j<5;j++)mesh(geo(new T.BoxGeometry(.31-j%2*.09,.018,.008)),standard(0x5d9dc1,.4),page,-.035,.18-j*.08,.014);}
 const cost=group("HOME:cost");for(let stack=0;stack<3;stack++)for(let i=0;i<3+stack*3;i++){const coin=mesh(geo(new T.CylinderGeometry(.20,.20,.045,40)),gold,cost,(stack-1)*.32,-.31+i*.048,stack===1?.12:0);coin.rotation.y=i*.4;}
 // View-dependent rim light leaves the subject clear instead of painting a grey disc over it.
 const orbMaterial=mat(new T.ShaderMaterial({transparent:true,depthWrite:false,blending:T.AdditiveBlending,uniforms:{clock:{value:0}},vertexShader:`varying vec3 viewNormal;varying vec3 viewDirection;varying vec3 localPoint;void main(){vec4 p=modelViewMatrix*vec4(position,1.);viewNormal=normalize(normalMatrix*normal);viewDirection=normalize(-p.xyz);localPoint=position;gl_Position=projectionMatrix*p;}`,fragmentShader:`uniform float clock;varying vec3 viewNormal;varying vec3 viewDirection;varying vec3 localPoint;void main(){vec3 n=normalize(viewNormal);float rim=pow(1.-abs(dot(n,normalize(viewDirection))),2.6);float glint=pow(max(0.,dot(n,normalize(vec3(-.45+.08*sin(clock*.2),.62,1.)))),95.);float secondary=pow(max(0.,dot(n,normalize(vec3(.7,-.3,.55)))),65.);float arc=.65+.35*sin(atan(localPoint.y,localPoint.x)*5.-clock*.65);vec3 hue=mix(vec3(.12,.43,1.),vec3(.64,.26,1.),smoothstep(-.5,.6,localPoint.x));gl_FragColor=vec4(hue*(.5+rim*2.3)+vec3(.65,.83,1.)*glint*.65+hue*secondary*.25,clamp(rim*(.65+arc*.35)+glint*.55+secondary*.2,0.,1.));}`}));
 const shells:Record<string,Three.Mesh>={};
 for(const[id,g]of Object.entries(groups)){if(id==="HOME:product")continue;const shell=mesh(geo(new T.SphereGeometry(.78,40,28)),orbMaterial,g);shell.renderOrder=3;shells[id]=shell;}
 // The supplied PNGs already have alpha. Do not re-key dark chocolate or crop
 // their corners with a radial mask. A scene-atlas cell is a complete subject.
 const loader=new T.TextureLoader();
 const productTexture=loader.load("/home-art/product.png");productTexture.colorSpace=T.SRGBColorSpace;textures.push(productTexture);
 const atlasTexture=loader.load("/home-art/home-subjects-v2.png",loaded=>{
  if(disposed)return;
  const image=loaded.image as HTMLImageElement,canvas=document.createElement("canvas");canvas.width=image.width;canvas.height=image.height;
  const context=canvas.getContext("2d",{willReadFrequently:true});if(!context)return;context.drawImage(image,0,0);
  const pixels=context.getImageData(0,0,image.width,image.height).data,cw=Math.floor(image.width/3),ch=Math.floor(image.height/3);
  for(const[id,spec]of Object.entries(assetSubjects)){if(spec.cell<0||!shells[id]||!subjectMeshes[id])continue;const fit=fitSubjectBounds(pixels,image.width,(spec.cell%3)*cw,Math.floor(spec.cell/3)*ch,cw,ch,spec.width,spec.height);envelopes[id]=fit;subjectMeshes[id].position.set(-fit.centerX,-fit.centerY,.08);shells[id].scale.set(fit.radiusX/.78,fit.radiusY/.78,fit.radiusZ/.78);}
 });atlasTexture.colorSpace=T.SRGBColorSpace;textures.push(atlasTexture);
 const assetSubjects:Record<string,{cell:number;width:number;height:number}>={
  "HOME:product":{cell:-1,width:6.4,height:4.267},
  "HOME:ingredients":{cell:0,width:1.6,height:1.6},
  "HOME:manufacturing":{cell:4,width:1.65,height:1.65},
  "HOME:distribution":{cell:5,width:1.65,height:1.65},
  "HOME:evidence":{cell:6,width:1.6,height:1.6},
  "HOME:cost":{cell:7,width:1.6,height:1.6},
  "HOME:sugar":{cell:1,width:1.6,height:1.6},
  "HOME:dairy":{cell:2,width:1.6,height:1.6},
 };
 for(const[id,spec]of Object.entries(assetSubjects)){
  const parent=groups[id];for(const child of parent.children)if(child!==shells[id])child.visible=false;
  let texture=productTexture;
  if(spec.cell>=0){texture=atlasTexture.clone();texture.repeat.set(1/3,1/3);texture.offset.set((spec.cell%3)/3,1-(Math.floor(spec.cell/3)+1)/3);textures.push(texture);}
  const surface=mat(new T.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,side:T.DoubleSide,toneMapped:false}));
  const subject=mesh(geo(new T.PlaneGeometry(spec.width,spec.height)),surface,parent,0,0,.08);subject.renderOrder=2;
  subjectMeshes[id]=subject;
  if(id==="HOME:product")parent.rotation.set(0,0,0);
 }
 return{groups,shells,envelopes,update(time:number){orbMaterial.uniforms.clock.value=time;for(let i=0;i<attr.count;i++)attr.setZ(i,rest[i*3+2]+Math.sin(time*.7+rest[i*3+1]*3)*.017);attr.needsUpdate=true;foilGeo.computeVertexNormals();fragments.forEach((m,i)=>{m.rotation.y=time*.10+i*.4;m.rotation.x=time*.07+i});smoke.forEach((m,i)=>{const t=(time*.15+i/15)%1;m.position.set(-.35+(i%3)*.28+Math.sin(t*5+i)*.055,1+t*.5,-.09);m.scale.setScalar(.7+t*1.5);(m.material as Three.MeshBasicMaterial).opacity=(1-t)*.13});wheels.forEach(w=>w.rotation.y=time*.5);},dispose(){disposed=true;geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose())}};
}
