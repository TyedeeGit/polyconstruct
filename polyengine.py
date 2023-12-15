from polymetric import *


class Joint:
    def __init__(self, pos: Vector):
        self.pos = pos
        self.connections: list[Rod] = []

    def connect(self, rod):
        self.connections.append(rod)


class Rod:
    def __init__(self, j1: Joint, j2: Joint):
        self.j1 = j1
        self.j2 = j2
        j1.connect(self)
        j2.connect(self)
        self.length = get_distance(j1.pos, j2.pos)


class Truss:
    pass
