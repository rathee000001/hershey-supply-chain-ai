"use client";
import { useEffect, useRef } from "react";
import { createProceduralGalaxy } from "./reference/procedural-galaxy";
import { createInteractiveStarfield } from "./reference/interactive-starfield";
import {useSceneSession} from "./SceneSession";

export default function HomeCosmos({ chapter, paused, world="home" }: { chapter: number; paused: boolean; world?: "home"|"supply"|"evidence"|"cost"|"sources"|"method" }) {
  const focus=useSceneSession();
  const host = useRef<HTMLDivElement>(null);
  const state = useRef({ chapter, paused, world, detail:Boolean(focus.session) });
  useEffect(() => { state.current = { chapter, paused, world, detail:Boolean(focus.session) }; }, [chapter, paused, world, focus.session]);
  useEffect(() => {
    const element = host.current!;
    let disposed = false, cleanup = () => {};
    import("three").then(T => {
      if (disposed) return;
      let renderer: InstanceType<typeof T.WebGLRenderer>;
      try { renderer = new T.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "low-power" }); }
      catch { element.dataset.fallback = "true"; return; }
      renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
      element.appendChild(renderer.domElement);
      const scene = new T.Scene(), camera = new T.PerspectiveCamera(40, 1, .1, 150);
      camera.position.z = 15;
      const galaxy = createProceduralGalaxy(T), stars = createInteractiveStarfield(T, innerWidth < 700 ? 900 : 2100, 180);
      scene.add(galaxy.display, stars.group);
      const world = new T.Matrix4(), point = new T.Vector3();
      const resize = () => { const w=element.clientWidth,h=element.clientHeight; renderer.setSize(w,h); camera.aspect=w/h;camera.updateProjectionMatrix();galaxy.resize(w,h); };
      resize();const observer=new ResizeObserver(resize);observer.observe(element);
      const pointer=(event:PointerEvent)=>{const x=event.clientX/innerWidth*2-1,y=1-event.clientY/innerHeight*2;stars.pointer(x,y);galaxy.uniforms.uPointer.value.set(x,y);};
      const lost=(e:Event)=>{e.preventDefault();element.dataset.fallback="true";};
      window.addEventListener("pointermove",pointer,{passive:true});document.addEventListener("pointerleave",stars.leave);renderer.domElement.addEventListener("webglcontextlost",lost);
      let frame=0,last=0,time=0,progress=0,oldChapter=0,transition=4;
      const tick=(now:number)=>{
        frame=requestAnimationFrame(tick);
        const dt=Math.min(.035,(now-last)/1000||.016);last=now;
        if(document.hidden)return;
        const active=state.current;
        if(Math.floor(active.chapter)!==oldChapter){oldChapter=Math.floor(active.chapter);transition=0;}
        if(!active.paused){time+=dt;transition+=dt;progress+=(active.chapter-progress)*Math.min(1,dt*2);}
        const telemetry=focus.flow.current,samples=telemetry.samples;
        const amount=active.paused||active.detail||!samples.length?0:.6*Math.sin(Math.PI*telemetry.mix)**2;
        stars.update(dt,camera,progress,active.paused,{amount,matrix:world,point:(t)=>{
          const sample=samples[Math.min(samples.length-1,Math.floor(t*samples.length))];
          if(!sample)return point.set(0,0,-10);
          const halfHeight=15*Math.tan(Math.PI*20/180);
          return point.set(sample.x*halfHeight*camera.aspect,sample.y*halfHeight,0);
        }});
        galaxy.uniforms.uWorld.value={home:0,supply:1,evidence:2,cost:3,sources:4,method:5}[active.world];
        galaxy.uniforms.uTime.value=time;galaxy.uniforms.uProgress.value=progress*2;
        galaxy.render(renderer);renderer.render(scene,camera);
        element.dataset.chapter=String(active.chapter);element.dataset.transfer=amount.toFixed(2);
      };frame=requestAnimationFrame(tick);
      cleanup=()=>{cancelAnimationFrame(frame);observer.disconnect();window.removeEventListener("pointermove",pointer);document.removeEventListener("pointerleave",stars.leave);renderer.domElement.removeEventListener("webglcontextlost",lost);stars.dispose();galaxy.dispose();renderer.dispose();renderer.domElement.remove();};
    });
    return()=>{disposed=true;cleanup();};
  },[]);
  return <div ref={host} className="hc-cosmos" aria-hidden="true" />;
}
