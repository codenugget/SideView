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

class Program:
    def __init__(self):
        self.program = -1

        self.pos_attrib = -1
        self.nrm_attrib = -1
        self.uv_attrib = -1
        self.Mproj_uform = -1
        self.Mmodel_uform = -1
        self.col_uform = -1
        self.bkg_uform = -1
        self.fresnel_uform = -1

    def run(self, Mproj, Mmodel, base_color, bkg_color, fresnel):
        glUseProgram(self.program) # This activates the shader
        glUniformMatrix4fv(self.Mproj_uform, 1, GL_FALSE, Mproj)
        glUniformMatrix4fv(self.Mmodel_uform, 1, GL_FALSE, Mmodel)
        glUniform4fv(self.col_uform, 1, [base_color])
        glUniform4fv(self.bkg_uform, 1, [bkg_color]) 
        glUniform4fv(self.fresnel_uform, 1, [fresnel])

    def destroy(self):
        glDeleteProgram(self.program)

def create():
    ret = Program()
    # Compile The Program and shaders
    ret.program = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(VERTEX_SHADER,GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))
    #glBindFragDataLocation(ret.program,0,"fragColor");

    ret.pos_attrib = glGetAttribLocation(ret.program, 'position')
    ret.uv_attrib = glGetAttribLocation(ret.program, 'uv')
    ret.nrm_attrib = glGetAttribLocation(ret.program, 'normal')
    ret.Mproj_uform = glGetUniformLocation(ret.program, 'Mproj')
    ret.Mmodel_uform = glGetUniformLocation(ret.program, 'Mmodel')
    ret.col_uform = glGetUniformLocation(ret.program, 'color')
    ret.bkg_uform = glGetUniformLocation(ret.program, 'colorBack')
    ret.fresnel_uform = glGetUniformLocation(ret.program, 'fresnel')

    return ret
create.__doc__ = "Creates a very simple color shader using glsl. Returns: color_shader.Param that contains the program, attrib, and uniform locations"
