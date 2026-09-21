"use client";
import {useEffect,useRef} from "react";
import type * as Three from "three";
import {useSceneSession} from "./SceneSession";

/**
 * Home's approved artwork is the color/detail source, not a replacement UI.
 * GLSL separates distant nebula and near silhouettes; route particles are live geometry.
 * This is a texture-based scene, not a claim of procedural reconstruction of the art.
 */
export default function ApprovedHomeUniverse({paused,progress,artPath="/home-art/home-universe-reference.png",worldName="home"}:{paused:boolean;progress:number;artPath?:string;worldName?:string}){
 const focus=useSceneSession();
 const mount=useRef<HTMLDivElement>(null);
 const live=useRef({paused,progress,detail:false});
 live.current={paused,progress,detail:Boolean(focus.session)};
 useEffect(()=>{
  const host=mount.current;if(!host)return;
  let cancelled=false,cleanup=()=>{};
  import("three").then(T=>{
   if(cancelled)return;
   let renderer:Three.WebGLRenderer;
   try{renderer=new T.WebGLRenderer({alpha:false,antialias:true,powerPreference:"low-power"})}
   catch{host.dataset.fallback="true";return}
   renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=T.SRGBColorSpace;
   host.append(renderer.domElement);
   const scene=new T.Scene(),camera=new T.OrthographicCamera(-1,1,1,-1,.1,10);camera.position.z=2;
   const uniforms={art:{value:null as Three.Texture|null},time:{value:0},aspect:{value:1},imageAspect:{value:1918/820},pointer:{value:new T.Vector2()},chapter:{value:0}};
   const texture=new T.TextureLoader().load(artPath,loaded=>{
    if(cancelled)return;
    uniforms.imageAspect.value=loaded.image.width/loaded.image.height;
    host.dataset.artReady="true";
   },undefined,()=>{host.dataset.fallback="true"});
   texture.colorSpace=T.SRGBColorSpace;texture.minFilter=T.LinearFilter;uniforms.art.value=texture;
   const geometry=new T.PlaneGeometry(2,2);
   const material=new T.ShaderMaterial({
    depthTest:false,depthWrite:false,toneMapped:false,uniforms,
    vertexShader:"varying vec2 screenUv;void main(){screenUv=uv;gl_Position=vec4(position.xy,.999,1.);}",
    fragmentShader:`varying vec2 screenUv;
     uniform sampler2D art;uniform float time,aspect,imageAspect,chapter;uniform vec2 pointer;
     vec2 cover(vec2 uv){vec2 scale=vec2(min(1.,aspect/imageAspect),min(1.,imageAspect/aspect));return (uv-.5)*scale+.5;}
     void main(){
      vec2 uv=cover(screenUv);
      float foreground=1.-smoothstep(.13,.31,uv.y);
      float horizon=smoothstep(.76,.94,uv.x)*(1.-smoothstep(.28,.62,uv.y));
      float nearMask=max(foreground,horizon);
      vec2 farShift=pointer*vec2(.0024,.0018);
      vec2 nearShift=pointer*vec2(.006,.0035);
      float field=(1.-nearMask)*smoothstep(.24,.58,uv.x);
      vec2 drift=vec2(sin(uv.y*15.+time*.035),cos(uv.x*13.-time*.029))*.00085*field;
      vec2 chapterShift=vec2(sin(chapter*1.3)*.003,cos(chapter*.8)*.002-.002);
      vec3 farColor=texture2D(art,clamp(uv+farShift+drift+chapterShift,vec2(.002),vec2(.998))).rgb;
      vec3 nearColor=texture2D(art,clamp(uv+nearShift,vec2(.002),vec2(.998))).rgb;
      vec3 color=mix(farColor,nearColor,nearMask);
      float illumination=1.+.028*sin(time*.18+uv.x*8.-uv.y*7.)*field;
      color*=illumination;
      // Protect the reading column without flattening the illuminated scene.
      color*=mix(.58,1.,smoothstep(.25,.64,screenUv.x));
      gl_FragColor=vec4(color,1.);
      #include <colorspace_fragment>
     }`
   });
   const sky=new T.Mesh(geometry,material);sky.frustumCulled=false;sky.renderOrder=-1;scene.add(sky);
   let seed=1379;const random=()=>{seed=seed*16807%2147483647;return(seed-1)/2147483646};
   const count=280,positions=new Float32Array(count*3),seeds=Array.from({length:count},()=>({x:random()*2-1,y:random()*2-1,phase:random()*Math.PI*2,speed:.2+random()*.7}));
   const particleGeometry=new T.BufferGeometry();particleGeometry.setAttribute("position",new T.BufferAttribute(positions,3));
   const alpha=new Float32Array(count),sizes=new Float32Array(count);for(let i=0;i<count;i++)sizes[i]=1.3+random()*2.1;
   particleGeometry.setAttribute("strength",new T.BufferAttribute(alpha,1));particleGeometry.setAttribute("size",new T.BufferAttribute(sizes,1));
   const particleMaterial=new T.ShaderMaterial({transparent:true,depthWrite:false,blending:T.AdditiveBlending,toneMapped:false,
    vertexShader:"attribute float strength;attribute float size;varying float opacity;void main(){opacity=strength;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);gl_PointSize=size;}",
    fragmentShader:"varying float opacity;void main(){float r=length(gl_PointCoord-.5)*2.;float glow=pow(max(0.,1.-r),2.);gl_FragColor=vec4(.6,.78,1.,glow*opacity);}"
   });
   const particles=new T.Points(particleGeometry,particleMaterial);particles.frustumCulled=false;scene.add(particles);
   const resize=()=>{renderer.setSize(innerWidth,innerHeight);uniforms.aspect.value=innerWidth/innerHeight};
   resize();window.addEventListener("resize",resize);
   let mx=0,my=0,time=0,last=0,frame=0,displayChapter=0,transfer=0;
   const pointer=(event:PointerEvent)=>{mx=event.clientX/innerWidth-.5;my=.5-event.clientY/innerHeight};
   window.addEventListener("pointermove",pointer,{passive:true});
   const animate=(now:number)=>{
    frame=requestAnimationFrame(animate);const dt=Math.min(.04,(now-last)/1000||.016);last=now;if(document.hidden)return;
    const state=live.current,flow=focus.flow.current;
    if(!state.paused){
     time+=dt;
     if(!state.detail)displayChapter+=(state.progress-displayChapter)*Math.min(1,dt*3);
     uniforms.pointer.value.lerp(new T.Vector2(mx,my),Math.min(1,dt*3));
     if(!state.detail)transfer=Math.sin(Math.PI*flow.mix)**2*.85;
     const chapter=Math.min(3,Math.floor(flow.progress)),samples=flow.samples;
     for(let i=0;i<count;i++){
      const seed=seeds[i],k=i*3;
      const driftX=Math.sin(time*.015*seed.speed+seed.phase)*.009,driftY=Math.cos(time*.012+seed.phase)*.006;
      let x=seed.x+driftX,y=seed.y+driftY;
      if(i<150&&samples.length){
       const offset=Math.floor(time*(chapter===2?3:1.1)+i*.73)%12;
       const sample=samples[((i%samples.length)*12+offset)%samples.length];
       x+=(sample.x-x)*transfer;y+=(sample.y-y)*transfer;
      }
      positions[k]=x;positions[k+1]=y;positions[k+2]=0;
      alpha[i]=(.16+.16*(.5+.5*Math.sin(time*.6+seed.phase)))+(i<150?transfer*.45:0);
     }
     particleGeometry.attributes.position.needsUpdate=true;particleGeometry.attributes.strength.needsUpdate=true;
    }
    uniforms.time.value=time;uniforms.chapter.value=displayChapter;
    renderer.render(scene,camera);
    host.dataset.world="approved-"+worldName+"-textured-depth";host.dataset.motionTime=time.toFixed(3);host.dataset.particleTransfer=transfer.toFixed(3);host.dataset.flowChapter=String(Math.floor(flow.progress));
   };
   frame=requestAnimationFrame(animate);
   cleanup=()=>{cancelAnimationFrame(frame);window.removeEventListener("resize",resize);window.removeEventListener("pointermove",pointer);geometry.dispose();material.dispose();texture.dispose();particleGeometry.dispose();particleMaterial.dispose();renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove()};
  }).catch(()=>{host.dataset.fallback="true"});
  return()=>{cancelled=true;cleanup()};
 },[artPath,worldName]);
 return <div ref={mount} className="approved-home-universe" aria-hidden="true"/>;
}
