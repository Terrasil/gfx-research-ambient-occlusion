#version 430 core
#include "views.glsl"
#include "camera.glsl"
#include "gbuffer.glsl"
uniform sampler2D uSignal,uDetails;
layout(location=0) out vec4 image;
void main() {
    camera();
    ivec2 xy=ivec2(gl_FragCoord.xy);
    vec4 g=positionAt(xy);
    float a=texelFetch(uSignal,xy,0).r;
    vec3 c=vec3(a);
    if(uDisplay==0) c=g.w>0?material(int(g.w),g.xyz,normalAt(xy))*(.19+.81*a):sky(primaryRay(xy));
    if(uDisplay==2) { vec4 w=texelFetch(uDetails,xy,0); c=vec3(w.z/(24.0*uBudget),w.y/(6.0*uBudget),.06); }
    image=vec4(toDisplay(c),1);
}
