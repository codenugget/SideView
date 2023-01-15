class ObjParse:
    def __init__(self, filename, verbose):
        self.filename = filename
        fp = open(filename, 'r')

        self.lines = [line.strip().split() for line in fp.readlines()]
        fp.close()

        self.vertices = []
        self.normals = []
        self.uvs = []

        self.face_vtx = []
        self.face_uv = []
        self.face_nrm = []

        warned = set()
        #line_nr = 0
        for line in self.lines:
            #line_nr = line_nr + 1
            if not line or line[0].startswith('#'):
                continue
            if line[0] == 'v':
                self.vertices.append(self.parse_vertex(line))
            elif line[0] == 'vn':
                self.normals.append(self.parse_normal(line))
            elif line[0] == 'vt':
                self.uvs.append(self.parse_texture(line))
            elif line[0] == 'f':
                poly_indices = self.parse_face(line)
                for attribs in poly_indices:
                    self.face_vtx.append(attribs[0])
                    self.face_uv.append(attribs[1])
                    self.face_nrm.append(attribs[2])

            else:
                if verbose and not line[0] in warned:
                    print(f"{line[0]} is not supported")
                    warned.add(line[0])

    def parse_vertex(self, line):
        dims = len(line) - 1
        v = []
        for i in range(dims):
            v.append(float(line[i+1]))
        return v
    def parse_normal(self, line):
        dims = len(line) - 1
        v = []
        for i in range(dims):
            v.append(float(line[i+1]))
        return v
    def parse_texture(self, line):
        dims = len(line) - 1
        v = []
        for i in range(dims):
            v.append(float(line[i+1]))
        return v
    def parse_face(self, line):
        dim = len(line) - 1
        poly = []
        for i in range(dim):
            idx = []
            sp = line[i+1].split('/')
            for e in line[i+1].split('/'):
                if e:
                    idx.append(int(e) - 1) # -1 since they start with 1
                else:
                    idx.append(int(-1)) # set negative index when no data is there
            poly.append(idx)
        return poly
ObjParse.__doc__ = "A very simplified obj parser. Only reads the arrays and do not group them etc. arrays after parsing: vertices, normals, uvs, faces"
