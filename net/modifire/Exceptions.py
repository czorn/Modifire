

class InvalidBlockFaceException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Attempted Value %i " % (self.value)