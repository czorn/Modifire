
class BlockGeom():
    """ A struct that represents the data needed to create
    the geometries for a Block.
    """
     
    def __init__(self):
        self.vertex = []
        self.texcoord = []
        self.prim = []
        self.normal = []
        self.lighttex = []
        self.blockFace = None