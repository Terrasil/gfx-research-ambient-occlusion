#version 430 core
#include "views.glsl"
#include "camera.glsl"
#include "gbuffer.glsl"
#include "sampling.glsl"
layout(location=0) out vec4 signal;
#ifdef DIAGNOSTICS
layout(location=1) out vec4 details;
#endif
int probes=0, supportPairs=0;
float neighborSupport(ivec2 xy,vec3 p,vec3 n,ivec2 step) {
    ivec2 q=xy+step;
    if(!inside(q)) return 0.0;
    ++supportPairs;
    vec4 g=positionAt(q);
    if(g.w==0.0) return 0.0;
    // Point-to-plane distance discounts depth changes on an inclined flat surface.
    float tol=max(.01*uParameter,2.0*pixelSize(p));
    return float(abs(dot(g.xyz-p,n))<=tol && dot(normalAt(q),n)>=.85);
}
float localThickness(ivec2 xy, vec3 p) {
    vec3 n=normalAt(xy);
    float h=neighborSupport(xy,p,n,ivec2(-1,0))+neighborSupport(xy,p,n,ivec2(1,0));
    float v=neighborSupport(xy,p,n,ivec2(0,-1))+neighborSupport(xy,p,n,ivec2(0,1));
    float confidence=uMethod==5?.25*(h+v):.5*min(h,v);
    if(uMethod==6) {
        // Orientation ablation: four axes instead of two. Opposite-pair support
        // uses the same point-to-plane/normal criteria as the archived method.
        float d0=neighborSupport(xy,p,n,ivec2(-1,-1))+neighborSupport(xy,p,n,ivec2(1,1));
        float d1=neighborSupport(xy,p,n,ivec2(-1,1))+neighborSupport(xy,p,n,ivec2(1,-1));
        confidence=.5*max(max(h,v),max(d0,d1));
    }
    return uParameter*mix(.06,.75,confidence*confidence);
}
bool screenBlocked(vec3 p,vec3 n,vec3 d) {
    for(int j=1;j<=6;++j) {
        vec3 x=p+.003*uParameter*n+d*(float(j)*uParameter/6.0);
        ivec2 xy; if(!screenPixel(x,xy)) break;
        ++probes;
        vec4 g=positionAt(xy);
        if(g.w==0.0 || dot(g.xyz-p,n)<.002*uParameter || length(g.xyz-p)>uParameter) continue;
        float gap=zView(x)-zView(g.xyz);
        if(gap<=.002*uParameter || gap>.75*uParameter) continue;
        float cap=.25*uParameter;
        if(uMethod==0) cap=.06*uParameter;
        if(uMethod==2) cap=.75*uParameter;
        if(uMethod==7) cap=.40*uParameter;
        if(uMethod==8) cap=.55*uParameter;
        if(uMethod==3 || uMethod==5 || uMethod==6) {
            if(gap<=.06*uParameter) return true;
            cap=localThickness(xy,g.xyz);
        }
        if(gap<=cap) return true;
    }
    return false;
}
float horizonOcclusion(vec3 p,vec3 n,float rotation) {
    vec3 t=normalize(cross(abs(n.y)<.9?vec3(0,1,0):vec3(1,0,0),n));
    vec3 b=cross(n,t);
    float total=0;
    for(int i=0;i<uBudget;++i) {
        float a=2.0*pi*(float(i)/float(uBudget)+rotation);
        vec3 dir=cos(a)*t+sin(a)*b; float h=0;
        for(int j=1;j<=6;++j) {
            ivec2 xy;
            if(!screenPixel(p+dir*(float(j)*uParameter/6.0),xy)) break;
            ++probes;
            vec4 g=positionAt(xy);
            vec3 v=g.xyz-p; float r=length(v);
            if(g.w>0 && r>.002*uParameter && r<=uParameter && dot(dir,v)>0.0)
                h=max(h,dot(n,v)/r);
        }
        total+=h*h;
    }
    return total/float(uBudget);
}
void main() {
    camera();
    ivec2 xy=ivec2(gl_FragCoord.xy);
    vec4 g=positionAt(xy); float visibility=1.0;
    if(g.w>0) {
        vec3 n=normalAt(xy);
        vec2 rotation=shift(xy,uint(uSeed));
        if(uMethod==4) visibility-=horizonOcclusion(g.xyz,n,rotation.y);
        else {
            float blocked=0;
            for(int i=0;i<uBudget;++i)
                if(screenBlocked(g.xyz,n,cosineRay(i,uBudget,rotation,n))) ++blocked;
            visibility-=blocked/float(uBudget);
        }
    }
    signal=vec4(vec3(visibility),1);
#ifdef DIAGNOSTICS
    details=vec4(float(g.w>0),float(probes),float(supportPairs),0);
#endif
}
