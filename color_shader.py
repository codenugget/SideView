from OpenGL.GL import *
import OpenGL.GL.shaders

VERTEX_SHADER ="""
#version 330
uniform mat4 Mproj;
uniform mat4 Mmodel;
uniform vec4 color;
uniform vec4 colorBack;

// x=bias, y=scale, z=power, w=reserved
uniform vec4 fresnel;

in vec4 position;
in vec2 uv;
in vec3 normal;

out vec4 frgColor;
out float Rfresnel;
void main() {
    mat4 Mnormal = transpose(inverse(Mmodel));

    vec3 n = vec3(Mnormal * vec4(normal, 0.0));
    vec3 p = vec3(Mmodel * position);
    vec3 e = -normalize(p);

    float L_eye = dot(n, e);

    float bias = fresnel.x;
    float scale = fresnel.y;
    float power = fresnel.z;

    Rfresnel = bias + scale * pow(1.0 - abs(L_eye), power);
    Rfresnel = min(max(Rfresnel, 0.0), 1.0);

    // make sure the back is slightly visible
    if (L_eye < 0)
        L_eye = -L_eye * fresnel.w;
    float diffuse = L_eye;

    frgColor.xyz = color.rgb * diffuse;
    frgColor.a = color.a;
    frgColor.a = frgColor.a + uv.r - uv.r;
    gl_Position = Mproj * vec4(p, 1.0);
}
"""
FRAGMENT_SHADER = """
#version 330
uniform vec4 colorBack;

in vec4 frgColor;
in float Rfresnel;
void main() {
    //gl_FragColor = vec4(0.0f, 1.0f, 0.0f,1.0f);
    vec4 result = mix(frgColor, colorBack, Rfresnel);
    result.a = frgColor.a;
    gl_FragColor = result;
}
"""

def create():
    # Compile The Program and shaders
    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(VERTEX_SHADER,GL_VERTEX_SHADER),
                                            OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))
    glBindFragDataLocation(shader,0,"fragColor");

    position = glGetAttribLocation(shader, 'position')
    uv = glGetAttribLocation(shader, 'uv')
    nrm = glGetAttribLocation(shader, 'normal')
    proj = glGetUniformLocation(shader, 'Mproj')
    model = glGetUniformLocation(shader, 'Mmodel')
    color = glGetUniformLocation(shader, 'color')
    colorBack = glGetUniformLocation(shader, 'colorBack')
    fresnel = glGetUniformLocation(shader, 'fresnel')

    return shader, position, uv, nrm, proj, model, color, colorBack, fresnel
create.__doc__ = """Creates a very simple color shader using glsl. Returns:
  ShaderProgram,
  PosAttrib, UVAttrib, NrmAttrib,
  ProjUform, ModelUform, ColUform, BkgColUform, FresnelUForm"""
