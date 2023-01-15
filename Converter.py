from OpenGL.GL import *

import numpy as np
import ObjParse as op

class TriSoup:
    def __init__(self, verts, uvs, norms, face_vtx, face_uv, face_nrm):
        self.vao = -1
        self.vertex_buffer_object = -1
        self.pos_attrib = -1
        self.uv_attrib = -1
        self.nrm_attrib = -1
        self.orig_vertices = verts
        self.has_uv = len(face_uv) > 0
        self.has_nrm = len(face_nrm) > 0
        if len(face_vtx) == 0:
            raise Exception("Must have vertices")
        if self.has_uv and len(face_vtx) != len(face_uv):
            raise Exception("Number of indices must be the same for both vertices and uvs")
        if self.has_nrm and len(face_vtx) != len(face_nrm):
            raise Exception("Number of indices must be the same for both vertices and normals")

        self.num_attribs = 3
        if self.has_uv:
            self.num_attribs += 2
        if self.has_nrm:
            self.num_attribs += 3
        self.num_floats = self.num_attribs * len(face_vtx)
        self.vertex_data = np.zeros([1, self.num_floats], dtype = np.float32).flatten()

        for i in range(len(face_vtx)):
            idx = face_vtx[i]
            val_x = verts[idx * 3 + 0]
            val_y = verts[idx * 3 + 1]
            val_z = verts[idx * 3 + 2]
            self.vertex_data[i * self.num_attribs + 0] = val_x
            self.vertex_data[i * self.num_attribs + 1] = val_y
            self.vertex_data[i * self.num_attribs + 2] = val_z
            o = 3

            if self.has_uv:
                idx = face_uv[i]
                val_x = uvs[idx * 2 + 0]
                val_y = uvs[idx * 2 + 1]
                self.vertex_data[i * self.num_attribs + o + 0] = val_x
                self.vertex_data[i * self.num_attribs + o + 1] = val_y
                o += 2

            if self.has_nrm:
                idx = face_nrm[i]
                val_x = norms[idx * 3 + 0]
                val_y = norms[idx * 3 + 1]
                val_z = norms[idx * 3 + 2]
                self.vertex_data[i * self.num_attribs + o + 0] = val_x
                self.vertex_data[i * self.num_attribs + o + 1] = val_y
                self.vertex_data[i * self.num_attribs + o + 2] = val_z
                o += 3

    def calc_center(self):
        n = int(len(self.orig_vertices) / 3)
        x = 0
        y = 0
        z = 0
        for idx in range(n):
            x = x + self.orig_vertices[idx * 3 + 0]
            y = y + self.orig_vertices[idx * 3 + 1]
            z = z + self.orig_vertices[idx * 3 + 2]
        x = x / n
        y = y / n
        z = z / n
        #print([x, y, z])
        return np.array([x, y, z])

    def count_verts(self):
        return int(self.num_floats / self.num_attribs)
    def count_attrib_bytes(self):
        return self.num_attribs * 4
    def count_bytes(self):
        return self.num_floats * 4

    def create_geom(self, pos_attrib, uv_attrib, nrm_attrib):
        # Create buffer object
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vertex_buffer_object = glGenBuffers(1)

        # Bind the buffer and setup the attrib arrays
        vertex_attrib_bytes = self.count_attrib_bytes()
        num_array_bytes = self.count_bytes()

        self.pos_attrib = pos_attrib
        self.uv_attrib = uv_attrib
        self.nrm_attrib = nrm_attrib

        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_object)
        glBufferData(GL_ARRAY_BUFFER, num_array_bytes, self.vertex_data, GL_STATIC_DRAW)

        glVertexAttribPointer(pos_attrib, 3, GL_FLOAT, GL_FALSE, vertex_attrib_bytes, None)
        glEnableVertexAttribArray(pos_attrib)
        skip_bytes = 3 * 4

        if self.has_uv:
            glVertexAttribPointer(uv_attrib, 2, GL_FLOAT, GL_FALSE, vertex_attrib_bytes, ctypes.c_void_p(skip_bytes))
            glEnableVertexAttribArray(uv_attrib)
            skip_bytes += 2 * 4

        if self.has_nrm:
            glVertexAttribPointer(nrm_attrib, 3, GL_FLOAT, GL_FALSE, vertex_attrib_bytes, ctypes.c_void_p(skip_bytes))
            glEnableVertexAttribArray(nrm_attrib)
            skip_bytes += 3 * 4

    def use(self):
        #print(self.vertex_buffer_object)
        glBindVertexArray(self.vao)

    def destroy(self):
        glDeleteBuffers(1, [self.vertex_buffer_object])
        glDeleteVertexArrays(1, [self.vao])

def convert_tris(o):
    if not isinstance(o, op.ObjParse) or not o.vertices:
        return None
    if len(o.vertices[0]) != 3:
        raise Exception("Only supporting vertex dimension 3")
    verts = np.array(o.vertices).flatten()
    face_vtx = np.array(o.face_vtx)
    uvs = None
    face_uv = []
    if o.uvs:
        if len(o.uvs[0]) != 2:
            raise Exception("Only supporting uv dimension 2")
        uvs = np.array(o.uvs).flatten()
        face_uv = np.array(o.face_uv)
    norms = None
    face_nrm = []
    if o.normals:
        if len(o.normals[0]) != 3:
            raise Exception("Only supporting normals dimension 3")
        norms = np.array(o.normals).flatten()
        face_nrm = np.array(o.face_nrm)
    return TriSoup(verts, uvs, norms, face_vtx, face_uv, face_nrm)
