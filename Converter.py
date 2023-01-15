import numpy as np
import ObjParse as op

class TriSoup:
    def __init__(self, verts, uvs, norms, face_vtx, face_uv, face_nrm):
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

    def count_verts(self):
        return int(self.num_floats / self.num_attribs)
    def count_attrib_bytes(self):
        return self.num_attribs * 4
    def count_bytes(self):
        return self.num_floats * 4

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
