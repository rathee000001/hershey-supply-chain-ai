export type SubjectEnvelope={centerX:number;centerY:number;radiusX:number;radiusY:number;radiusZ:number};
/** Fit a padded ellipsoid to visible artwork, without stretching or cropping it. */
export function fitSubjectBounds(pixels:Uint8ClampedArray|Uint8Array,imageWidth:number,cellX:number,cellY:number,cellWidth:number,cellHeight:number,worldWidth:number,worldHeight:number):SubjectEnvelope{
 const samples:Array<[number,number]>=[];let left=Infinity,right=-Infinity,top=-Infinity,bottom=Infinity;
 for(let y=0;y<cellHeight;y+=2)for(let x=0;x<cellWidth;x+=2){if(pixels[((cellY+y)*imageWidth+cellX+x)*4+3]<32)continue;const px=((x+.5)/cellWidth-.5)*worldWidth,py=(.5-(y+.5)/cellHeight)*worldHeight;samples.push([px,py]);left=Math.min(left,px);right=Math.max(right,px);top=Math.max(top,py);bottom=Math.min(bottom,py);}
 if(!samples.length)return{centerX:0,centerY:0,radiusX:worldWidth*.55,radiusY:worldHeight*.55,radiusZ:Math.min(worldWidth,worldHeight)*.45};
 const centerX=(left+right)/2,centerY=(top+bottom)/2,rx=Math.max(.08,(right-left)/2),ry=Math.max(.08,(top-bottom)/2);
 let extent=1;for(const[x,y]of samples)extent=Math.max(extent,Math.hypot((x-centerX)/rx,(y-centerY)/ry));
 const padding=extent*1.1;
 return{centerX,centerY,radiusX:rx*padding,radiusY:ry*padding,radiusZ:Math.min(rx,ry)*padding*.82};
}
