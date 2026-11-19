#version 430 core
#include "views.glsl"
#include "camera.glsl"
#include "geometry.glsl"
#include "objects.glsl"
#include "gbuffer.glsl"
#include "sampling.glsl"
uniform int uOffset,uTotal,uChunk;
layout(location=0) out vec4 signal;
layout(location=1) out vec4 details;
void main() {
    camera();
    ivec2 xy=ivec2(gl_FragCoord.xy);
    vec4 g=positionAt(xy);
    vec3 n=normalAt(xy);
    float blocked=0;
    if(g.w>0) {
        vec2 rotation=shift(xy,0x62461u+uint(uSeed));
        vec3 origin=g.xyz+.003*uParameter*n;
        for(int j=0;j<uChunk;++j) {
            vec3 d=cosineRay(uOffset+j,uTotal,rotation,n);
            if(trace(origin,d,uParameter).id>0) ++blocked;
        }
    }
    signal=vec4(vec3(1.0-blocked/float(uChunk)),1);
    details=vec4(float(g.w>0),0,0,0);
}
