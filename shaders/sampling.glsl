uint mixBits(uint s) {
    s^=s>>16u; s*=0x7feb352du; s^=s>>15u; s*=0x846ca68bu; return s^(s>>16u);
}
vec2 shift(ivec2 p,uint stream) {
    uint k=mixBits(uint(p.x)+65537u*uint(p.y)+stream*0x9e3779b9u);
    return vec2(mixBits(k),mixBits(k^0x51ed270bu))*(1.0/4294967296.0);
}
vec3 cosineRay(int i,int count,vec2 rotation,vec3 n) {
    vec2 u=fract(vec2((float(i)+.5)/float(count),float(bitfieldReverse(uint(i)))*2.3283064365386963e-10)+rotation);
    float a=2.0*pi*u.y, r=sqrt(u.x);
    vec3 t=normalize(cross(abs(n.y)<.9?vec3(0,1,0):vec3(1,0,0),n));
    return normalize(t*(r*cos(a))+cross(n,t)*(r*sin(a))+n*sqrt(1.0-u.x));
}
