#!/usr/bin/env python3
"""Build IBRA RACING V12 from the preserved V11 archive extraction."""
from pathlib import Path

ROOT = Path.cwd()
SRC_DIR = ROOT / "v11"
files = sorted((p for p in SRC_DIR.rglob("*.html") if p.name != "index.html"), key=lambda p: p.stat().st_size, reverse=True)
if not files:
    raise SystemExit("V11 source HTML not found")
src = files[0]
s = src.read_text(encoding="utf-8", errors="strict")

if "IBRA_V12_GLTF_INTEGRATION" in s:
    raise SystemExit("V12 integration marker already present in source")

needle = "</script>\n<script>\n(function(){\n'use strict';"
if s.count(needle) != 1:
    raise SystemExit(f"Could not identify main script insertion point: {s.count(needle)}")
s = s.replace(needle, "</script>\n<script src=\"https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js\"></script>\n<script>\n(function(){\n'use strict';", 1)

css_needle = "#wheel{position:absolute;left:46%;bottom:-118px;width:236px;height:236px;margin-left:-118px;transform:rotate(0deg);filter:drop-shadow(0 4px 8px #000a)}"
css = r"""
/* IBRA_V12_GLTF_INTEGRATION: cockpit details */
#cab .seat{position:absolute;bottom:-3%;width:24%;height:35%;z-index:1;pointer-events:none;border:1px solid #454a52;border-bottom:0;border-radius:46% 46% 12% 12%;background:linear-gradient(110deg,#080a0d 0%,#242a32 38%,#101318 72%,#050608 100%);box-shadow:inset 0 0 18px #000,0 0 18px #0009}
#cab .seat:before{content:"";position:absolute;left:23%;top:-20%;width:54%;height:42%;border:1px solid #414750;border-radius:44% 44% 25% 25%;background:linear-gradient(110deg,#090b0e,#303741 48%,#0b0d11);box-shadow:inset 0 0 12px #000}
#cab .seat:after{content:"";position:absolute;left:18%;right:18%;top:22%;height:3px;border-radius:4px;background:linear-gradient(90deg,transparent,#a52b35aa,transparent)}
#cab .seat-left{left:-10%;transform:skew(-8deg) rotate(3deg)}
#cab .seat-right{right:-10%;transform:skew(8deg) rotate(-3deg)}
#cab .dash-panel{position:absolute;z-index:3;left:13%;right:13%;bottom:7%;height:15%;border:1px solid #3a414a;border-bottom:0;border-radius:18px 18px 7px 7px;background:linear-gradient(180deg,#303740 0%,#171c23 35%,#080a0e 100%);box-shadow:0 -5px 22px #000b,inset 0 2px 7px #ffffff12;pointer-events:none}
#cab .dash-topline{position:absolute;left:7%;right:7%;top:10%;height:2px;background:linear-gradient(90deg,transparent,#5b6572,#9b3038,#5b6572,transparent);opacity:.8}
#cab .cluster{position:absolute;left:50%;top:13%;transform:translateX(-50%);width:56%;height:70%;display:flex;align-items:center;justify-content:center;gap:7%;}
#cab .gauge{width:29%;aspect-ratio:1;border-radius:50%;border:3px solid #4c5663;background:radial-gradient(circle,#101923 0 48%,#05080d 70%);box-shadow:0 0 9px #28a9ff66,inset 0 0 10px #168dce66;display:flex;align-items:center;justify-content:center;position:relative;color:#8ee4ff;font:800 clamp(10px,2.2vw,18px)/1 monospace;text-shadow:0 0 8px #28baff}
#cab .gauge:before{content:"";position:absolute;inset:5px;border:1px solid #2a8db7;border-radius:50%;opacity:.75}
#cab .gauge small{position:absolute;bottom:16%;font:700 6px/1 system-ui;color:#9ab4c5;letter-spacing:1px}
#cab .dash-screen{min-width:24%;height:54%;border:1px solid #235b78;border-radius:5px;background:linear-gradient(135deg,#071b27,#0b3448);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#8ce8ff;box-shadow:0 0 12px #00aaff55;font:800 11px/1.1 monospace;text-shadow:0 0 7px #00baff}
#cab .dash-screen small{font:600 6px/1.2 system-ui;letter-spacing:1px;color:#b7d7e2}
#cab.has-model-wheel #wheel{display:none}
@media(max-width:600px){#cab .seat{width:27%;height:31%}#cab .dash-panel{left:8%;right:8%;height:14%;bottom:7%}#cab .cluster{width:62%;gap:5%}#cab .gauge{border-width:2px}}
"""
if s.count(css_needle) != 1:
    raise SystemExit("Could not identify cabin CSS insertion point")
s = s.replace(css_needle, css_needle + css, 1)

html_needle = '<div id="cab"><div class="roof"></div><div class="pl"></div><div class="pr"></div><div class="dash"></div>'
html_add = '''<div id="cab"><div class="roof"></div><div class="pl"></div><div class="pr"></div><div class="dash"></div>
<div class="seat seat-left"></div><div class="seat seat-right"></div>
<div class="dash-panel"><div class="dash-topline"></div><div class="cluster"><div class="gauge"><span id="dashSpeed">0</span><small>KM/H</small></div><div class="dash-screen"><span id="dashGear">P</span><small>IBRA M3</small></div><div class="gauge"><span id="dashRpm">0</span><small>RPM x1000</small></div></div></div>'''
if s.count(html_needle) != 1:
    raise SystemExit("Could not identify cabin HTML insertion point")
s = s.replace(html_needle, html_add, 1)

engine_needle = "var camera=new THREE.PerspectiveCamera(62,window.innerWidth/window.innerHeight,0.5,2600);"
engine_add = r'''var camera=new THREE.PerspectiveCamera(62,window.innerWidth/window.innerHeight,0.5,2600);
/* IBRA_V12_GLTF_INTEGRATION: real steering wheel in first-person cabin */
scene.add(camera);
var wheelPivot=new THREE.Group(),wheelModelReady=false;
wheelPivot.position.set(0,-0.38,-1.0);camera.add(wheelPivot);
var assetLoader=(typeof THREE.GLTFLoader==='function')?new THREE.GLTFLoader():null;
if(assetLoader){
  assetLoader.load('../sports-steering-wheel.glb',function(gltf){
    var model=gltf.scene;model.updateMatrixWorld(true);
    var bounds=new THREE.Box3().setFromObject(model),center=bounds.getCenter(new THREE.Vector3());
    model.position.sub(center);model.scale.setScalar(1.55);
    model.traverse(function(o){if(o.isMesh){o.castShadow=true;o.frustumCulled=false;}});
    wheelPivot.add(model);wheelModelReady=true;$('cab').classList.add('has-model-wheel');
  },undefined,function(e){console.warn('IBRA V12: steering wheel GLB unavailable; SVG fallback kept.',e);});
}
function requestHighwayModel(){
  if(!assetLoader||highwayLoadStarted||highwayAssetAdded)return;
  highwayLoadStarted=true;
  assetLoader.load('../highway-segment.glb',function(gltf){highwayGltf=gltf;addHighwayModel(gltf);},undefined,function(e){highwayLoadStarted=false;console.warn('IBRA V12: highway GLB unavailable; original Conakry road kept.',e);});
}'''
if s.count(engine_needle) != 1:
    raise SystemExit("Could not identify camera initialization point")
s = s.replace(engine_needle, engine_add, 1)

state_needle = "var ckRS=null,ckRoads=null,carY=0,FREE=true;"
state_add = r'''var ckRS=null,ckRoads=null,carY=0,FREE=true,ckGroup=null,highwayGltf=null,highwayAssetAdded=false,highwayLoadStarted=false;
function addHighwayModel(gltf){
  if(!gltf||highwayAssetAdded)return;
  highwayGltf=gltf;
  if(!ckGroup)return;
  var root=gltf.scene;root.updateMatrixWorld(true);
  var count=24,start=145*Math.PI/180,step=23.6/470;
  var up=new THREE.Vector3(0,1,0),base=new THREE.Object3D();
  root.traverse(function(mesh){
    if(!mesh.isMesh)return;
    var inst=new THREE.InstancedMesh(mesh.geometry,mesh.material,count);
    inst.count=count;inst.frustumCulled=false;inst.castShadow=false;inst.receiveShadow=false;
    for(var i=0;i<count;i++){
      var a=start+i*step;
      base.position.set(470*Math.cos(a),0.035,470*Math.sin(a));
      base.quaternion.setFromAxisAngle(up,a+Math.PI/2);base.scale.set(1,1,1);base.updateMatrix();
      var matrix=base.matrix.clone().multiply(mesh.matrixWorld);
      inst.setMatrixAt(i,matrix);
    }
    inst.instanceMatrix.needsUpdate=true;ckGroup.add(inst);
  });
  highwayAssetAdded=true;
}'''
if s.count(state_needle) != 1:
    raise SystemExit("Could not identify Conakry state insertion point")
s = s.replace(state_needle, state_add, 1)

ck_end = "ckGroup=new THREE.Group();scene.children.slice(n0).forEach(function(o){scene.remove(o);ckGroup.add(o);});scene.add(ckGroup);\n}"
ck_end_new = "ckGroup=new THREE.Group();scene.children.slice(n0).forEach(function(o){scene.remove(o);ckGroup.add(o);});scene.add(ckGroup);if(highwayGltf)addHighwayModel(highwayGltf);\n}"
if s.count(ck_end) != 1:
    raise SystemExit(f"Could not identify Conakry group finalization: {s.count(ck_end)}")
s = s.replace(ck_end, ck_end_new, 1)

map_needle = "loadMap=function(id){_loadMapOrig(id);buildPosts(id);setEnv();};"
map_add = "loadMap=function(id){_loadMapOrig(id);if(id==='conakry')requestHighwayModel();buildPosts(id);setEnv();};"
if s.count(map_needle) != 1:
    raise SystemExit("Could not identify map loader wrapper")
s = s.replace(map_needle, map_add, 1)

setview_needle = "$('bV').textContent='Vue : '+(CABIN?'Cabine':'Arrière');\n  car.visible=!CABIN;"
setview_add = "$('bV').textContent='Vue : '+(CABIN?'Cabine':'Arrière');\n  car.visible=!CABIN;wheelPivot.visible=CABIN;"
if s.count(setview_needle) != 1:
    raise SystemExit("Could not identify setView body")
s = s.replace(setview_needle, setview_add, 1)

frame_needle = "wheelEl.style.transform='rotate('+(S.steer*57.3*4).toFixed(1)+'deg)';"
frame_add = frame_needle + "if(wheelModelReady)wheelPivot.rotation.z=-S.steer*0.78;"
if s.count(frame_needle) != 1:
    raise SystemExit("Could not identify cabin steering update")
s = s.replace(frame_needle, frame_add, 1)

speed_needle = "var speedEl=$('speed'),gearEls=document.querySelectorAll('#gears span');"
speed_add = "var speedEl=$('speed'),gearEls=document.querySelectorAll('#gears span'),dashSpeedEl=$('dashSpeed'),dashGearEl=$('dashGear'),dashRpmEl=$('dashRpm');"
if s.count(speed_needle) != 1:
    raise SystemExit("Could not identify dashboard update declarations")
s = s.replace(speed_needle, speed_add, 1)
update_needle = "var g=Phys.gearOf(S,inp);\n  if(g!==lastGear)"
update_add = "var g=Phys.gearOf(S,inp);\n  if(dashSpeedEl)dashSpeedEl.textContent=String(Math.round(kmh));if(dashGearEl)dashGearEl.textContent=g;if(dashRpmEl)dashRpmEl.textContent=String(Math.min(8,Math.round(kmh/32+gasV*2)));\n  if(g!==lastGear)"
if s.count(update_needle) != 1:
    raise SystemExit("Could not identify gear update point")
s = s.replace(update_needle, update_add, 1)

s = s.replace("Nouveau : vue cabine avec volant, levier de vitesses en H, mode nuit avec phares et carte Montagne de nuit (boutons en haut).", "V12 : volant sport 3D, sièges visibles, tableau de bord lumineux et tronçon d’autoroute 3D à Conakry.")
s = s.replace("showOv('IBRA RACING v11'", "showOv('IBRA RACING v12'")

out_dir = ROOT / "v12"
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "IBRA_RACING_v12_cabine_autoroute.html"
out.write_text(s, encoding="utf-8")
redirect = '''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url=./IBRA_RACING_v12_cabine_autoroute.html"><title>IBRA RACING V12</title></head><body><p><a href="./IBRA_RACING_v12_cabine_autoroute.html">Ouvrir IBRA RACING V12 – Cabine et autoroute</a></p><script>location.replace("./IBRA_RACING_v12_cabine_autoroute.html");</script></body></html>'''
(out_dir / "index.html").write_text(redirect, encoding="utf-8")

assert "../sports-steering-wheel.glb" in s
assert "../highway-segment.glb" in s
assert "new THREE.InstancedMesh" in s
assert "dashSpeed" in s and "seat-right" in s
assert len(s) > 9_000_000
print(f"V12_PATCH_OK source={src} output={out} bytes={out.stat().st_size}")
print("V12_FEATURES=GLTF steering wheel; leather seat bolsters; live illuminated speed/gear cluster; lazy-loaded 24 instanced highway tiles on west Conakry arc; original streets retained")