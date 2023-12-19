import math

from .metricutils import *
from typing import List

__doc__ = """
Implement physics engine.
"""


class Matrix:
    def __init__(self, xx: float, xy: float, yx: float, yy: float):
        """
        Matrix[\n
        [xx, xy]\n
        [yx, yy]]
        :param xx:
        :param xy:
        :param yx:
        :param yy:
        """
        self.xx = xx
        self.xy = xy
        self.yx = yx
        self.yy = yy

    def __add__(self, other):
        return Matrix(self.xx + other.xx, self.xy + other.xy, self.yx + other.yx, self.yy + other.yy)

    def __neg__(self):
        return (-1) * self

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        """
        Matrix multiplication, or matrix vector multiplication.
        :param other:
        :return:
        """
        if isinstance(other, float) or isinstance(other, int):
            return Matrix(self.xx * other, self.xy * other, self.yx * other, self.yy * other)
        if isinstance(other, Matrix):
            return Matrix(
                Vector2(self.xx, self.xy) * Vector2(other.xx, other.yx),
                Vector2(self.xx, self.xy) * Vector2(other.xy, other.yy),
                Vector2(self.yx, self.yy) * Vector2(other.xx, other.yx),
                Vector2(self.yx, self.yy) * Vector2(other.xy, other.yy)
            )
        if isinstance(other, Vector2):
            return Vector2(
                self.xx * other.x + self.xy + other.y,
                self.yx * other.x + self.yy + other.y
            )

    def __rmul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return self * other

    @property
    def transpose(self):
        return Matrix(self.xx, self.yx, self.xy, self.yy)

    @property
    def trace(self):
        return self.xx + self.yy

    @property
    def determinant(self):
        return self.xx*self.yy - self.xy*self.yx

    @property
    def identity(self):
        return Matrix(1, 0, 0, 1)


class StressTensor(Matrix):
    def __init__(self, xx: float, xy: float, yy: float):
        super().__init__(xx, xy, xy, yy)

    def __add__(self, other):
        return StressTensor(self.xx + other.xx, self.xy + other.xy, self.yy + other.yy)

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return StressTensor(self.xx * other, self.xy * other, self.yy * other)
        else:
            return super().__mul__(other)

    @staticmethod
    def from_matrix(m: Matrix):
        """
        Returns a stress tensor from a symmetric matrix.
        :param m:
        :return:
        """
        if m.xy != m.yx:
            raise ValueError("Matrix must be symmetric for it to be a valid stress tensor!")
        return StressTensor(m.xx, m.xy, m.yy)

    @property
    def identity(self):
        return StressTensor.from_matrix(super().identity)

    @property
    def invariants(self):
        return self.trace, self.xx * self.yy - self.xy**2, self.determinant

    @property
    def stress_deviator(self):
        return self - (1/3)*self.invariants[0]*self.identity


class Material:
    def __init__(self, material_name: str, strength: float, density: float):
        """
        A physical material.
        :param material_name:
        :param strength:
        """
        self.material_name = material_name
        self.strength = strength
        self.density = density


class Joint:
    def __init__(self, pos: Vector2, material: Material, radius: float, thickness: float):
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
        self.forces: List[Vector2] = []

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
    def __init__(self, initial_state: State, total_time: float, dt: float = 0.01):
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

    def __next__(self) -> Union[StopIteration, tuple[State, State]]:
        if self.done:
            self.simulating = False
            raise StopIteration
        else:
            return self.step()

    def step(self) -> tuple[State, State]:
        """
        Simulate the next frame.
        :return:
        """
        self.current_frame += 1
        # Actually simulate what happens here
        return self.current_state, self.previous_state

    @property
    def current_time(self) -> float:
        return self.current_frame * self.dt

    @property
    def done(self) -> bool:
        return self.current_frame == len(self)-1

    @property
    def current_state(self) -> State:
        return self.record[self.current_frame]

    @property
    def previous_state(self) -> State:
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
            return None, self.current_state
        self.current_frame += 1
        return self.current_state, self.previous_state
