import pygame
from polymetric import *


class Joint:
    def __init__(self, pos: Vector):
        self.pos = pos
        self.connections: list[Rod] = []

    def connect(self, rod):
        pass

class Rod:
    def __init__(self, j1: Joint, j2: Joint):
        self.j1 = j1
        self.j2 = j2
        self.length = get_distance(j1.pos, j2.pos)

class Truss:
    pass


print(round(get_angle((1, 0), (0, 2), center=(1, 1), unit='deg'), 2))