from polymetric import *

"""
Implement physics engine.
"""


class Joint:
    def __init__(self, pos: Vector2):
        """
        A joint that connects one or more rods.
        :param pos:
        """
        self.pos = pos
        self.connections: list[Rod] = []

    def connect(self, rod):
        """
        Connect a rod to the joint.
        :param rod:
        :return:
        """
        self.connections.append(rod)


class Rod:
    def __init__(self, j1: Joint, j2: Joint):
        """
        A rod connecting two joints.
        :param j1:
        :param j2:
        """
        self.j1 = j1
        self.j2 = j2
        j1.connect(self)
        j2.connect(self)
        self.length = get_distance(j1.pos, j2.pos)
