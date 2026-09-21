"use client";
import {useEffect,useMemo,useRef,useState,type CSSProperties} from "react";
import type * as Three from "three";
import Image from "next/image";
import {BookOpen,Boxes,Coins,Factory,FileSearch,Leaf,Network,Truck,Users,FlaskConical,Info,Candy,Bean,Milk,Package,Warehouse,Store,FileCog,Database,ShieldCheck,ChartNoAxesCombined,PanelsTopLeft} from "lucide-react";
import {HersheyOrb as Orb} from "./HersheyOrb";
import {scenePosition,type JourneyChapter,type JourneyItem,type JourneyEdge} from "./scene-model";
import {useSceneSession} from "./SceneSession";
import {createHomeGeometry} from "./home-geometry";
import {SubjectGlass,storyObjectFor} from "./StoryObject";

type Props={chapters:JourneyChapter[];progress:number;paused:boolean;onSelect:(item:JourneyItem)=>void;onEdge?:(edge:JourneyEdge)=>void;visible:boolean;interactive?:boolean;homeModels?:boolean;luminous?:boolean;connectionStyle?:"bundle"|"constellation"};
const smooth=(v:number)=>{const t=Math.max(0,Math.min(1,v));return t*t*(3-2*t)};
const iconFor=(item:JourneyItem)=>item.id==="method-0"?BookOpen:item.id==="method-1"?FileCog:item.id==="method-2"?Database:item.id==="method-3"?ShieldCheck:item.id==="method-4"?Boxes:item.id==="method-5"?Network:item.id==="method-6"?ChartNoAxesCombined:item.id==="method-7"?PanelsTopLeft:item.id==="NODE_ORIGIN_SUGAR"?Candy:item.id==="NODE_ORIGIN_COCOA"?Bean:item.id==="NODE_ORIGIN_DAIRY"?Milk:/PACKAGING|WRAPPING/.test(item.id)?Package:/WAREHOUSE/.test(item.id)?Warehouse:/RETAILER/.test(item.id)?Store:item.id==="NODE_CONSUMER"?Users:item.id==="HOME:people"?Users:item.id==="HOME:minor"?FlaskConical:item.id==="HOME:study"?Info:item.kind==="cost"||item.id.startsWith("NODE_COST")?Coins:item.kind==="source"?BookOpen:item.kind==="evidence"?FileSearch:item.kind==="ingredient"||/ORIGIN|ING_/.test(item.id)?Leaf:/PROCESS|MANUFACTUR/.test(item.id)?Factory:/RETAIL|DISTRIBUT|CARRIER|WAREHOUSE/.test(item.id)?Truck:item.kind==="method"?Network:Boxes;
export default function LivingFlowScene(props:Props){
 const host=useRef<HTMLDivElement>(null),canvas=useRef<HTMLDivElement>(null),anchors=useRef(new Map<string,HTMLButtonElement>()),edgeAnchors=useRef(new Map<string,HTMLButtonElement>());
 const focus=useSceneSession(),live=useRef({...props,session:focus.session});
 live.current={...props,session:focus.session};
 const pose=useRef({progress:0,chapter:0}),[ready,setReady]=useState(false),[failed,setFailed]=useState(false);
 const pool=useMemo(()=>Array.from(new Map(props.chapters.flatMap(c=>c.items).map(n=>[n.id,n])).values()),[props.chapters]);
 const allEdges=useMemo(()=>Array.from(new Map(props.chapters.flatMap(c=>c.edges).map(e=>[e.id,e])).values()),[props.chapters]);
 useEffect(()=>{
  const element=host.current,canvasElement=canvas.current;if(!element||!canvasElement)return;
  let gone=false,dispose=()=>{};
  Promise.all([import("three"),import("three/examples/jsm/environments/RoomEnvironment.js")]).then(([T,{RoomEnvironment}])=>{
   if(gone)return;
   let renderer:Three.WebGLRenderer;try{renderer=new T.WebGLRenderer({alpha:true,antialias:true,powerPreference:"high-performance"})}catch{setFailed(true);return}
   renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;canvasElement.append(renderer.domElement);
   const scene=new T.Scene(),root=new T.Group(),camera=new T.OrthographicCamera(-5.9,5.9,4.9,-4.9,.1,70);camera.position.z=20;scene.add(root);
   const room=new RoomEnvironment(),pmrem=new T.PMREMGenerator(renderer),environment=pmrem.fromScene(room,.04);scene.environment=environment.texture;scene.environmentIntensity=props.homeModels?.65:1.7;room.dispose();pmrem.dispose();
   scene.add(new T.HemisphereLight(0xc8ebff,0x201438,2));const key=new T.DirectionalLight(0xe8f8ff,4),rim=new T.DirectionalLight(0xb5a0ff,3);key.position.set(-3,4,6);rim.position.set(5,-2,3);scene.add(key,rim);if(props.homeModels){key.intensity=1.6;rim.intensity=1.3;}
   const nativeHome=props.homeModels?createHomeGeometry(T):null;if(nativeHome)Object.values(nativeHome.groups).forEach(group=>root.add(group));
   const constellation=props.connectionStyle==="constellation";const segments=72,strands=constellation?3:5,centerStrand=Math.floor(strands/2);
   const flowClock={value:0};
   const homeFlowMaterial=(core:boolean)=>new T.ShaderMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,blending:T.AdditiveBlending,toneMapped:false,uniforms:{clock:flowClock,fade:{value:1},core:{value:core?1:0}},vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,fragmentShader:`varying vec2 vUv;uniform float clock,fade,core;void main(){float edge=abs(vUv.y-.5)*2.;float feather=pow(max(0.,1.-edge),2.);float head=fract(vUv.x-clock*.12);float packet=exp(-pow((head-.5)*65.,2.));vec3 color=mix(vec3(.36,.58,1.),vec3(.48,.86,1.),vUv.x);color=mix(color,vec3(.88,.97,1.),packet*.1+core*.65);float light=mix(.25,1.4,core)+packet*.15;gl_FragColor=vec4(color*light,feather*fade);\n#include <colorspace_fragment>\n}`});
   const ribbons=new Map<string,{parts:Array<{mesh:Three.Mesh;geometry:Three.BufferGeometry;positions:Float32Array;normals:Float32Array}>;outer:Three.Material;inner:Three.Material;beads:Three.Mesh[]}>();
   const beadGeometry=new T.SphereGeometry(.017,8,6),beadMaterial=new T.MeshBasicMaterial({color:0xe4f6ff});
   const ensure=(id:string)=>{
    if(ribbons.has(id))return ribbons.get(id)!;
    const route=props.chapters.flatMap(c=>c.edges).find(edge=>edge.id===id),source=props.chapters.flatMap(c=>c.items).find(item=>item.id===route?.source);const tint=new T.Color(source?.color||"#8bdeff"); const outer=constellation?new T.MeshBasicMaterial({color:tint,transparent:true,opacity:.22,side:T.DoubleSide,depthWrite:false,blending:T.AdditiveBlending,toneMapped:false}):new T.MeshPhysicalMaterial({color:0xc9dce9,emissive:0x688caf,emissiveIntensity:.22,metalness:.58,roughness:.17,clearcoat:1,clearcoatRoughness:.07,transparent:true,opacity:.64,side:T.DoubleSide,depthWrite:false});
    const inner=constellation?new T.MeshBasicMaterial({color:tint.clone().lerp(new T.Color("#f0faff"),.55),transparent:true,opacity:.95,side:T.DoubleSide,depthWrite:false,blending:T.AdditiveBlending,toneMapped:false}):new T.MeshPhysicalMaterial({color:0xe4edf6,emissive:0x94bad5,emissiveIntensity:.28,metalness:.76,roughness:.14,clearcoat:1,transparent:true,opacity:.86,side:T.DoubleSide,depthWrite:false});
    const parts=Array.from({length:strands},(_,strand)=>{const positions=new Float32Array((segments+1)*6),normals=new Float32Array(positions.length),indices:number[]=[];for(let j=0;j<segments;j++){const n=j*2;indices.push(n,n+1,n+2,n+1,n+3,n+2)}const geometry=new T.BufferGeometry();geometry.setAttribute("position",new T.BufferAttribute(positions,3));geometry.setAttribute("normal",new T.BufferAttribute(normals,3));geometry.setIndex(indices);const uv=new Float32Array((segments+1)*4);for(let k=0;k<=segments;k++)uv.set([k/segments,0,k/segments,1],k*4);geometry.setAttribute("uv",new T.BufferAttribute(uv,2));const mesh=new T.Mesh(geometry,strand===centerStrand?inner:outer);mesh.frustumCulled=false;root.add(mesh);return{mesh,geometry,positions,normals}});
    const beads=Array.from({length:2},()=>{const mesh=new T.Mesh(beadGeometry,beadMaterial);root.add(mesh);return mesh});
    const value={parts,outer,inner,beads};ribbons.set(id,value);return value;
   };
   // The product/subject plane belongs to the SAME scene root as ribbons and node anchors.
   const artGeometry=new T.PlaneGeometry(1,1),artMeshes:Three.Mesh[]=[],textures:Three.Texture[]=[];
   const loader=new T.TextureLoader();
   const productTexture=props.homeModels?null:loader.load("/home-art/product.png"),atlasTexture=props.homeModels?null:loader.load("/home-art/scene-atlas.png");if(productTexture&&atlasTexture){productTexture.colorSpace=T.SRGBColorSpace;atlasTexture.colorSpace=T.SRGBColorSpace;textures.push(productTexture,atlasTexture);}
   for(let art=-1;!props.homeModels&&art<6;art++){
    const texture=art===-1?productTexture:atlasTexture;
    const material=new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{map:{value:texture},alpha:{value:0}},vertexShader:"varying vec2 uvOut;void main(){uvOut=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}",fragmentShader:`uniform sampler2D map;uniform float alpha;varying vec2 uvOut;void main(){vec2 p=uvOut;vec2 texUv=p;${art>=0?`texUv=p*vec2(.3333333,.5)+vec2(${((art%3)/3).toFixed(8)},${(1-(Math.floor(art/3)+1)/2).toFixed(8)});`:""} vec4 c=texture2D(map,texUv);gl_FragColor=vec4(c.rgb,alpha*c.a);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}`});
    const mesh=new T.Mesh(artGeometry,material);mesh.renderOrder=2;mesh.position.z=.35;root.add(mesh);artMeshes.push(mesh);
   }
   let width=1,height=1,worldHeight=9.8,frame=0,last=0,time=0,display=0,yaw=0,pitch=0,shownYaw=0,shownPitch=0,drag=false,lastX=0,lastY=0;
   const resize=()=>{width=Math.max(1,element.clientWidth);height=Math.max(1,element.clientHeight);renderer.setSize(width,height,false);{worldHeight=11.8*height/width;camera.top=worldHeight/2;camera.bottom=-worldHeight/2;camera.updateProjectionMatrix()}};
   const ro=new ResizeObserver(resize);ro.observe(element);resize();
   const down=(e:PointerEvent)=>{if(live.current.paused||live.current.session||e.target instanceof Element&&e.target.closest("button,a"))return;drag=true;lastX=e.clientX;lastY=e.clientY;element.setPointerCapture(e.pointerId)};
   const move=(e:PointerEvent)=>{if(!drag)return;yaw=Math.max(-.18,Math.min(.18,yaw+(e.clientX-lastX)*.001));pitch=Math.max(-.12,Math.min(.12,pitch-(e.clientY-lastY)*.0008));lastX=e.clientX;lastY=e.clientY};
   const up=()=>{drag=false};const reset=()=>{drag=false;yaw=0;pitch=0};
   element.addEventListener("pointerdown",down);element.addEventListener("pointermove",move);element.addEventListener("pointerup",up);element.addEventListener("pointercancel",up);window.addEventListener("scroll",reset,{passive:true});
   const vector=(p:{x:number;y:number})=>new T.Vector3((p.x-50)/10,(50-p.y)*worldHeight/122.5,0);
   const layout=(chapter:JourneyChapter)=>new Map(chapter.items.map((item,i)=>[item.id,scenePosition(chapter,item,i)]));
   const artSize=(chapter:JourneyChapter,item:JourneyItem)=>{const p=scenePosition(chapter,item,chapter.items.findIndex(n=>n.id===item.id));return Math.min(chapter.art===-1?5:chapter.pattern==="library"?4.3:3.2,Math.max(1.45,Math.min(p.x,100-p.x)/100*18))};
   const radius=(item:JourneyItem|undefined,chapter:JourneyChapter,dx:number,dy:number)=>{
    if(item?.core)return artSize(chapter,item)/11.8*width*.36;
    const envelope=item&&nativeHome?.envelopes[item.id];
    if(envelope){const rx=envelope.radiusX*.94*width/11.8,ry=envelope.radiusY*.94*height/worldHeight,length=Math.hypot(dx,dy)||1;return 1/Math.hypot(dx/length/rx,dy/length/ry);}
    const subject=item&&anchors.current.get(item.id)?.querySelector<HTMLElement>(".subject-glass");
    if(subject){const length=Math.hypot(dx,dy)||1;return 1/Math.hypot(dx/length/(subject.offsetWidth/2),dy/length/(subject.offsetHeight/2));}
    return props.homeModels?.78*.94*width/11.8:innerWidth<=1000?23:36;
   };
   const curve=(chapter:JourneyChapter,id:string,map:ReturnType<typeof layout>)=>{
    const edge=chapter.edges.find(e=>e.id===id);if(!edge)return null;
    const a=map.get(edge.source),b=map.get(edge.target);if(!a||!b)return null;
    const start=vector(a),end=vector(b),dx=(end.x-start.x)*width/11.8,dy=-(end.y-start.y)*height/worldHeight,len=Math.max(1,Math.hypot(dx,dy));
    const sourceItem=chapter.items.find(n=>n.id===edge.source),targetItem=chapter.items.find(n=>n.id===edge.target);
    const dock=(center:Three.Vector3,other:Three.Vector3,item:JourneyItem)=>{const size=artSize(chapter,item),direction=other.x<center.x?-1:1;center.x+=direction*size*.31;center.y+=Math.max(-size*.13,Math.min(size*.13,(other.y-center.y)*.2));};
    if(sourceItem?.core)dock(start,end,sourceItem);if(targetItem?.core)dock(end,start,targetItem);
    const ra=sourceItem?.core?0:radius(sourceItem,chapter,dx,dy),rb=targetItem?.core?0:radius(targetItem,chapter,dx,dy),trim=Math.min(1,len/(ra+rb+20));
    start.x+=dx/len*ra*trim/width*11.8;start.y-=dy/len*ra*trim/height*worldHeight;end.x-=dx/len*rb*trim/width*11.8;end.y+=dy/len*rb*trim/height*worldHeight;
    const h1=start.clone().lerp(end,.35),h2=end.clone().lerp(start,.35),bend=Math.min(.6,start.distanceTo(end)*.22);
    h1.y+=bend;h2.y-=bend;h1.z=.15;h2.z=-.1;return new T.CubicBezierCurve3(start,h1,h2,end);
   };
   const point=new T.Vector3(),aPoint=new T.Vector3(),bPoint=new T.Vector3(),nextPoint=new T.Vector3(),projection=new T.Vector3();
   const put=(el:HTMLElement,p:Three.Vector3)=>{projection.copy(p).applyMatrix4(root.matrixWorld).project(camera);el.style.transform="translate3d("+((projection.x*.5+.5)*width).toFixed(2)+"px,"+((-projection.y*.5+.5)*height).toFixed(2)+"px,0) translate(-50%,-50%)"};
   const tick=(now:number)=>{
    frame=requestAnimationFrame(tick);const state=live.current;if(document.hidden||width<2||height<2||!state.visible&&!state.session){last=now;return}
    const dt=Math.min(.04,Math.max(.001,(now-last)/1000));last=now;if(!state.paused)time+=dt;flowClock.value=time;
    const lastChapter=state.chapters.length-1,target=Math.min(lastChapter,Math.max(0,state.session?.progress??state.progress));
    display=state.session?target:state.paused?target:display+(target-display)*(1-Math.exp(-dt*10));
    if(Math.abs(target-display)<.0001)display=target;
    const i=Math.min(lastChapter,Math.floor(display)),j=Math.min(lastChapter,i+1),mix=i===j?0:smooth(((display-i)-.55)/.45);
    const a=state.chapters[i],b=state.chapters[j];if(!a||!b)return;
    pose.current={progress:display,chapter:mix<.5?i:j};element.dataset.displayProgress=display.toFixed(3);element.dataset.displayChapter=String(pose.current.chapter);element.dataset.mix=mix.toFixed(3);
    const ma=layout(a),mb=layout(b),blendedMap=new Map<string,{x:number;y:number}>();
    for(const id of new Set([...ma.keys(),...mb.keys()])){const pa=ma.get(id)||mb.get(id)!,pb=mb.get(id)||ma.get(id)!;blendedMap.set(id,{x:pa.x+(pb.x-pa.x)*mix,y:pa.y+(pb.y-pa.y)*mix})}
    if(state.session){yaw=0;pitch=0}shownYaw+=(yaw-shownYaw)*.15;shownPitch+=(pitch-shownPitch)*.15;const ambient=state.session||state.paused?0:1;root.rotation.set(shownPitch+Math.sin(time*.17)*.022*ambient,shownYaw+Math.sin(time*.12)*.032*ambient,Math.sin(time*.1)*.008*ambient);root.updateMatrixWorld(true);element.dataset.manualRotation=(Math.abs(shownYaw)+Math.abs(shownPitch)).toFixed(4);
    if(!state.paused){key.position.set(-3+Math.sin(time*.32)*1.3,4+Math.cos(time*.26),6);rim.position.x=4+Math.cos(time*.21)*2}
    const currentEdges=new Set([...a.edges,...b.edges].map(e=>e.id));
    for(const [id,button]of edgeAnchors.current){if(!currentEdges.has(id)){button.style.visibility="hidden";button.style.opacity="0";button.tabIndex=-1;button.setAttribute("aria-hidden","true")}}
    for(const e of [...a.edges,...b.edges])ensure(e.id);
    const transferSamples:Array<{x:number;y:number}>=[];const screenRect=element.getBoundingClientRect();
    for(const[id,r]of ribbons){
     const ca=curve(a,id,blendedMap),cb=curve(b,id,blendedMap),opacity=(ca?1-mix:0)+(cb?mix:0);
     for(const part of r.parts)part.mesh.visible=currentEdges.has(id)&&opacity>.005;
     r.beads.forEach(x=>x.visible=opacity>.1);if(opacity<.005)continue;
     r.outer.opacity=(constellation?.22:.84)*opacity;r.inner.opacity=.96*opacity;
     if(r.outer instanceof T.ShaderMaterial)r.outer.uniforms.fade.value=opacity;
     if(r.inner instanceof T.ShaderMaterial)r.inner.uniforms.fade.value=opacity;
     const startCurve=ca||cb!,endCurve=cb||ca!;
     for(let sample=0;sample<12;sample++){const t=sample/11;startCurve.getPoint(t,aPoint);endCurve.getPoint(t,bPoint);projection.copy(aPoint).lerp(bPoint,mix).applyMatrix4(root.matrixWorld).project(camera);transferSamples.push({x:(screenRect.left+(projection.x*.5+.5)*width)/innerWidth*2-1,y:1-(screenRect.top+(-projection.y*.5+.5)*height)/innerHeight*2})}
     for(let strand=0;strand<strands;strand++){const ribbon=r.parts[strand];for(let k=0;k<=segments;k++){const t=k/segments;startCurve.getPoint(t,aPoint);endCurve.getPoint(t,bPoint);point.copy(aPoint).lerp(bPoint,mix);startCurve.getPoint(Math.min(1,t+.006),aPoint);endCurve.getPoint(Math.min(1,t+.006),bPoint);nextPoint.copy(aPoint).lerp(bPoint,mix);const dx=nextPoint.x-point.x,dy=nextPoint.y-point.y,length=Math.hypot(dx,dy)||1,nx=-dy/length,ny=dx/length,envelope=Math.sin(Math.PI*t),spread=(strand-centerStrand)*(constellation?.005:.07)*(.5+.5*envelope),wave=Math.sin(t*9-time*.65)*.012*envelope,half=(constellation?(strand===centerStrand?.009:.035):(strand===centerStrand?.042:.022))*(.35+.65*envelope),twist=Math.sin(t*6.28+time*.4)*.2;for(let side=0;side<2;side++){const at=k*6+side*3,off=spread+wave+(side?half:-half);ribbon.positions[at]=point.x+nx*off;ribbon.positions[at+1]=point.y+ny*off;ribbon.positions[at+2]=(Math.sin(t*5+time*.35)*.055+(strand-centerStrand)*.004)*envelope;ribbon.normals[at]=nx*Math.sin(twist);ribbon.normals[at+1]=ny*Math.sin(twist);ribbon.normals[at+2]=Math.cos(twist)}}ribbon.geometry.attributes.position.needsUpdate=true;ribbon.geometry.attributes.normal.needsUpdate=true;}
     r.beads.forEach((bead,k)=>{const t=(time*.11+k*.5)%1;startCurve.getPoint(t,aPoint);endCurve.getPoint(t,bPoint);bead.position.copy(aPoint).lerp(bPoint,mix)});
     const button=edgeAnchors.current.get(id);if(button){startCurve.getPoint(.5,aPoint);endCurve.getPoint(.5,bPoint);put(button,aPoint.lerp(bPoint,mix));button.style.opacity=String(opacity*.7);button.style.visibility=opacity>.8?"visible":"hidden";button.tabIndex=opacity>.8?0:-1;button.setAttribute("aria-hidden",String(opacity<=.8))}
    }
    for(const[id,el]of anchors.current){
     const pa=ma.get(id),pb=mb.get(id),opacity=(pa?1-mix:0)+(pb?mix:0);const fallback={x:50,y:50};point.copy(vector(pa||pb||fallback)).lerp(vector(pb||pa||fallback),mix);put(el,point);el.style.opacity=String(opacity);el.style.visibility=opacity>.04?"visible":"hidden";el.style.pointerEvents=opacity>.85?"auto":"none";el.tabIndex=opacity>.85?0:-1;el.setAttribute("aria-hidden",String(opacity<.1));
     const ca=a.items.find(n=>n.id===id)?.core,cb=b.items.find(n=>n.id===id)?.core;el.dataset.core=String(mix<.5?!!ca:!!cb);
     const visibleItem=(mix<.5?a.items:b.items).find(n=>n.id===id);const label=el.querySelector(".hf-label-name");if(visibleItem){el.setAttribute("aria-label",visibleItem.label);if(label&&label.textContent!==visibleItem.label)label.textContent=visibleItem.label;}
     if(visibleItem?.core){const chapter=mix<.5?a:b,size=artSize(chapter,visibleItem)*(state.homeModels&&id==="HOME:product"?6.4/5.2:1);el.style.width=Math.max(44,size*width/11.8)+"px";el.style.height=Math.max(44,size*(chapter.art===-1?.666:1)*height/worldHeight)+"px";}
     if(state.homeModels&&!((mix<.5?ca:cb))){const envelope=nativeHome?.envelopes[id],w=Math.max(42,(envelope?2*envelope.radiusX:1.56)*.94*width/11.8),h=Math.max(42,(envelope?2*envelope.radiusY:1.56)*.94*height/worldHeight);el.style.width=w+"px";el.style.height=h+"px";el.dataset.enclosure=envelope?"subject-fitted":"fallback";const orb=el.querySelector<HTMLElement>(".hershey-orb");orb?.style.setProperty("--hershey-orb-size",Math.min(w,h)+"px");}
    }
    if(nativeHome){
     if(!state.paused)nativeHome.update(time);
     for(const[id,group]of Object.entries(nativeHome.groups)){
      const pa=ma.get(id),pb=mb.get(id),na=a.items.find(n=>n.id===id),nb=b.items.find(n=>n.id===id),amount=(pa?1-mix:0)+(pb?mix:0);
      group.visible=amount>.01;if(!group.visible)continue;
      group.position.copy(vector(pa||pb!)).lerp(vector(pb||pa!),mix);
      const scaleFor=(item:JourneyItem|undefined,chapter:JourneyChapter)=>!item?0:item.core?(id==="HOME:product"?artSize(chapter,item)/5.2:2.65):id==="HOME:product"?.18:.94;
      group.scale.setScalar(scaleFor(na,a)*(1-mix)+scaleFor(nb,b)*mix);
      if(nativeHome.shells[id])nativeHome.shells[id].visible=!(mix<.5?na?.core:nb?.core);
      if(id!=="HOME:product")group.rotation.y=Math.sin(time*.18)*.12;
     }
    }
    artMeshes.forEach((mesh,artIndex)=>{const art=artIndex-1,va=a.art===art?1-mix:0,vb=b.art===art?mix:0;const alpha=va+vb;(mesh.material as Three.ShaderMaterial).uniforms.alpha.value=alpha*.93;mesh.visible=alpha>.005;if(!mesh.visible)return;const source=va>=vb?a:b,map=va>=vb?ma:mb,core=source.items.find(n=>n.core);if(core){mesh.position.copy(vector(map.get(core.id)!));mesh.position.z=.25;const size=artSize(source,core);mesh.scale.set(size,art===-1?size*.666:size,1)}else{mesh.visible=false}});
    focus.flow.current={samples:transferSamples,mix,progress:display};
    renderer.render(scene,camera);
   };frame=requestAnimationFrame(tick);setReady(true);
   const lost=(e:Event)=>{e.preventDefault();setFailed(true)};renderer.domElement.addEventListener("webglcontextlost",lost);
   dispose=()=>{nativeHome?.dispose();cancelAnimationFrame(frame);ro.disconnect();element.removeEventListener("pointerdown",down);element.removeEventListener("pointermove",move);element.removeEventListener("pointerup",up);element.removeEventListener("pointercancel",up);window.removeEventListener("scroll",reset);for(const r of ribbons.values()){r.parts.forEach(p=>p.geometry.dispose());r.outer.dispose();r.inner.dispose()}beadGeometry.dispose();beadMaterial.dispose();artMeshes.forEach(m=>(m.material as Three.Material).dispose());artGeometry.dispose();textures.forEach(t=>t.dispose());environment.dispose();renderer.domElement.removeEventListener("webglcontextlost",lost);renderer.dispose();renderer.domElement.remove()};
  }).catch(()=>{if(!gone)setFailed(true)});
  return()=>{gone=true;dispose()};
 },[]);
 const openItem=(item:JourneyItem,button:HTMLButtonElement)=>{if(props.interactive===false)return;focus.open(item,button,pose.current.progress,pose.current.chapter);props.onSelect(item)};
 const visibleChapter=props.chapters[Math.min(props.chapters.length-1,Math.floor(props.progress))];
 return <div ref={host} className="hf-scene" id="retained-flow-scene" data-ready={ready} data-detail-retained={!!focus.session} aria-label="Interactive flowing scene">
 <div ref={canvas} className="hf-canvas" aria-hidden="true"/>
 {!failed&&pool.map(item=>{const Icon=iconFor(item),subject=!props.homeModels&&!item.core&&!item.logoUrl?(item.artwork||storyObjectFor(item.id,item.kind)):undefined;return <button key={item.id} ref={el=>{if(el)anchors.current.set(item.id,el);else anchors.current.delete(item.id)}} className="hf-node" data-native-model={Boolean(props.homeModels&&!["HOME:minor","HOME:study"].includes(item.id))} disabled={props.interactive===false} data-selected={focus.session?.subject.id===item.id} data-scene-label={item.label} style={{"--tone":item.color} as CSSProperties} onClick={e=>openItem(item,e.currentTarget)} tabIndex={-1} aria-hidden="true" aria-haspopup="dialog" aria-label={item.label}>{subject?<SubjectGlass name={subject}/>:<Orb size={58} color={item.color} decorative>{item.logoUrl?<span className="hershey-company-mark"><Image src={item.logoUrl} alt="" width={48} height={32} unoptimized/></span>:<Icon size={26}/>}</Orb>}<span className="hf-label"><span className="hf-label-name">{item.label}</span>{item.tag&&<small>{item.tag}</small>}</span>{item.summary&&<span className="hf-hover-note">{item.summary}</span>}</button>})}
 {!failed&&allEdges.map(edge=><button ref={el=>{if(el)edgeAnchors.current.set(edge.id,el);else edgeAnchors.current.delete(edge.id)}} key={edge.id} className="hf-edge-target" disabled={props.interactive===false} tabIndex={-1} aria-hidden="true" aria-label={"Inspect connection: "+(edge.materialFlow||edge.tooltipText||edge.id)} title={edge.tooltipText} onClick={e=>{if(props.interactive===false)return;focus.open({id:edge.id,label:edge.materialFlow||"Connection",kind:"method",color:"#a6ddeb"},e.currentTarget,pose.current.progress,pose.current.chapter);props.onEdge?.(edge)}}><span>↗</span></button>)}
 {failed&&<div className="hf-fallback"><p>The interactive renderer is unavailable. Explore the same records below.</p>{visibleChapter.items.map(item=><button className="hc-pill" key={item.id} onClick={e=>openItem(item,e.currentTarget)}>{item.label}</button>)}</div>}
 </div>
}
