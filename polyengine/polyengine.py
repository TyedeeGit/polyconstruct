import math

from .metricutils import *
from .units import *
from typing import List

__doc__ = """
Implement physics engine.
"""


class Material:
    def __init__(self, material_name: str, strength: Pressure, density: Density):
        """
        A physical material.
        :param material_name:
        :param strength:
        """
        self.material_name = material_name
        self.strength = strength
        self.density = density


class Joint:
    def __init__(self, pos: PhysicalVector2, material: Material, radius: Length, thickness: Length):
        """
        A joint that connects one or more rods.
        :param pos:
        """
        self.pos = pos
        self.material = material
        self.radius = radius
        self.thickness = thickness
        self.mass = math.pi * radius**2 * thickness * material.density
        self.connections: List[Rod] = []
        self.forces: List[ForceVector] = []

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

class State:
    def __init__(self, frame: int):
        """
        State of a simulation.
        """
        self.frame = frame
        self.joints: List[Joint] = []
        self.rods: List[Rod] = []

    def __repr__(self):
        return f'State[{self.frame}]'

class Simulation:
    def __init__(self, initial_state: State, total_time: Time, dt: Time = (1 / 60) * second):
        self.dt = dt
        self.total_time = total_time
        self.current_frame = 0
        self.record = [State(i) for i in range(len(self))]
        self.record[0] = initial_state
        self.simulating = True

    def __len__(self) -> int:
        return int(self.total_time/self.dt)

    def __iter__(self):
        if self.simulating:
            return self
        else:
            return RecordedSimulation(self)

    def __next__(self):
        if self.done:
            self.simulating = False
            raise StopIteration
        else:
            return self.step()

    def step(self):
        """
        Simulate the next frame.
        :return:
        """
        self.current_frame += 1
        # Actually simulate what happens here
        return self.current_state, self.previous_state

    @property
    def done(self):
        return self.current_frame == len(self)-1

    @property
    def current_state(self):
        return self.record[self.current_frame]

    @property
    def previous_state(self):
        return self.record[self.current_frame - 1]

    @current_state.setter
    def current_state(self, value: State):
        self.record[self.current_frame] = value

    @previous_state.setter
    def previous_state(self, value: State):
        self.record[self.current_frame-1] = value

class RecordedSimulation(Simulation):
    def __init__(self, simulation: Simulation):
        super().__init__(simulation.record[0], simulation.total_time, dt=simulation.dt)
        self.record = simulation.record
        self.current_frame = 0
        self.recording = False

    def __iter__(self):
        raise ValueError("Recording is not iterable")

    def __next__(self):
        if self.done:
            raise StopIteration
        else:
            return self.step()

    def step(self):
        """
        Step the record by one frame.
        :return:
        """
        if self.done:
            return self.current_state, None
        self.current_frame += 1
        return self.current_state, self.previous_state
