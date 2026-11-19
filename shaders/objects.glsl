// One list defines intersections and distance-to-object contact masks.
const int maxObjects=12;
int objectCount() {
    const int count[5]=int[5](5,11,7,5,0);
    return count[uScene];
}
void shape(int i,out vec3 c,out vec3 h,out bool sphere) {
    sphere=false;
    if(uScene==0) {
        const vec3 centers[5]=vec3[5](vec3(-1.3,.90,-.1),vec3(.48,.56,.42),vec3(1.82,.73,-1.25),vec3(-.1,.65,-2.5),vec3(-1.0,.18,1.55));
        const vec3 sizes[5]=vec3[5](vec3(.84,.90,.84),vec3(.56),vec3(.75,.73,.72),vec3(1.55,.65,.28),vec3(.75,.18,.29));
        c=centers[i]; h=sizes[i]; sphere=i==1;
    } else if(uScene==1) {
        if(i<8) { c=vec3(-2.03+.58*i,1.0,-.32); h=vec3(.045,1.0,.09); }
        else if(i==8) { c=vec3(0,1.68,-.40); h=vec3(2.35,.065,.08); }
        else if(i==9) { c=vec3(.42,.62,-1.45); h=vec3(.62); sphere=true; }
        else { c=vec3(-1.05,.20,1.1); h=vec3(.72,.08,.23); }
    } else if(uScene==2) {
        if(i<4) { c=vec3(-1.15+.46*i,.16+.16*i,-.42); h=vec3(.23,.16+.16*i,1.1); }
        else if(i==4) { c=vec3(1.65,.92,-.45); h=vec3(.50,.92,1.1); }
        else if(i==5) { c=vec3(.20,.90,-1.62); h=vec3(2.15,.90,.12); }
        else { c=vec3(-.28,1.45,.45); h=vec3(.91,.10,.33); }
    } else {
        const vec3 cc[5]=vec3[5](vec3(-2.7,1.65,.0),vec3(1.5,.54,.2),vec3(3.0,1.35,-1.25),vec3(.20,.34,-2.4),vec3(3.3,.95,1.25));
        const vec3 hh[5]=vec3[5](vec3(.38,1.65,2.1),vec3(.54),vec3(.45,1.35,.65),vec3(2.4,.34,.3),vec3(.1,.95,.84));
        c=cc[i]; h=hh[i]; sphere=i==1;
    }
}
Hit trace(vec3 o,vec3 d,float limit) {
    Hit hit=miss(limit);
    groundHit(o,d,0.0,hit);
    for(int i=0;i<objectCount();++i) {
        vec3 c,h; bool sphere; shape(i,c,h,sphere);
        if(sphere) sphereHit(o,d,c,h.x,i+2,hit); else boxHit(o,d,c,h,i+2,hit);
    }
    return hit;
}
float contactMask(vec3 p,int id) {
    if(id!=1) return 0.0;
    float distanceToSolid=farLimit;
    for(int i=0;i<objectCount();++i) {
        vec3 c,h; bool sphere; shape(i,c,h,sphere);
        float d=sphere?length(p-c)-h.x:length(max(abs(p-c)-h,vec3(0)));
        distanceToSolid=min(distanceToSolid,d);
    }
    return float(distanceToSolid<=.20*uParameter);
}
