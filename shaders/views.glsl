void setView(int scene,int view,out vec3 e,out vec3 target) {
    const vec3 eyes[3]=vec3[3](vec3(4.1,3.1,6.9),vec3(-3.0,2.3,6.7),vec3(.45,1.5,6.2));
    e=eyes[view]; target=vec3(0,.65,-.4);
    if(scene==3) { e.x+=1.0; target.x+=1.2; }
}
