import math
from .metricutils import *
from .gridutils import *

class Material:
    def __init__(self, material_name: str, density: float, yield_strength: float, bulk_modulus: float, shear_modulus: float):
        """
        A physical material.
        :param material_name:
        :param yield_strength:
        """
        self.material_name = material_name
        self.yield_strength = yield_strength
        self.bulk_modulus = bulk_modulus
        self.shear_modulus = shear_modulus
        self.density = density


class Tensor:
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
        return Tensor(self.xx + other.xx, self.xy + other.xy, self.yx + other.yx, self.yy + other.yy)

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
            return Tensor(self.xx * other, self.xy * other, self.yx * other, self.yy * other)
        if isinstance(other, Tensor):
            return Tensor(
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
        return Tensor(self.xx, self.yx, self.xy, self.yy)

    @property
    def trace(self):
        return self.xx + self.yy

    @property
    def determinant(self):
        return self.xx*self.yy - self.xy*self.yx

    @staticmethod
    def identity():
        return Tensor(1, 0, 0, 1)

    @staticmethod
    def zero():
        return Tensor(0, 0, 0, 0)


class StressTensor(Tensor):
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
    def from_matrix(m: Tensor):
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


def partial_derivative(grid: Grid[DataCell[float]], dx: float, x_index: float, y_index: float, direction: str):
    neighborhood = grid.get_neighbors(x_index, y_index)
    match direction:
        case 'x':
            if x_index == 0:
                return (neighborhood.get_cell(2, 1).data - neighborhood.get_cell(1, 1).data)/dx
            if x_index == grid.column_end:
                return (neighborhood.get_cell(1, 1).data - neighborhood.get_cell(0, 1).data) / dx
            return (neighborhood.get_cell(2, 1).data - neighborhood.get_cell(0, 1).data)/dx
        case 'y':
            if y_index == 0:
                return (neighborhood.get_cell(1, 2).data - neighborhood.get_cell(1, 1).data)/dx
            if y_index == grid.row_end:
                return (neighborhood.get_cell(1, 1).data - neighborhood.get_cell(1, 0).data)/dx
            return (neighborhood.get_cell(1, 2).data - neighborhood.get_cell(1, 0).data)/dx
        case _:
            raise ValueError("Invalid direction")


def vector_gradient(grid: Grid[DataCell[Vector2]], dx: float, x_index: float, y_index: float) -> Tensor:
    gx = Grid(grid.column_end + 1, grid.row_end + 1, DataCell, Vector2(0, 0))
    gy = Grid(grid.column_end + 1, grid.row_end + 1, DataCell, Vector2(0, 0))
    for column in gx.cells:
        for cell in column:
            cell.data = grid.get_cell(cell.x, cell.y).data.x
    for column in gy.cells:
        for cell in column:
            cell.data = grid.get_cell(cell.x, cell.y).data.y
    pxx = partial_derivative(gx, dx, x_index, y_index, 'x')
    pxy = partial_derivative(gx, dx, x_index, y_index, 'y')
    pyx = partial_derivative(gy, dx, x_index, y_index, 'x')
    pyy = partial_derivative(gy, dx, x_index, y_index, 'y')
    return Tensor(pxx, pxy, pyx, pyy)


def vector_divergence(grid: Grid[DataCell[Vector2]], dx: float, x_index: float, y_index: float):
    return vector_gradient(grid, dx, x_index, y_index).trace


def tensor_divergence(grid: Grid[DataCell[Tensor]], dx: float, x_index: float, y_index: float) -> Vector2:
    gx = Grid(grid.column_end+1, grid.row_end+1, DataCell, Vector2(0, 0))
    gy = Grid(grid.column_end+1, grid.row_end+1, DataCell, Vector2(0, 0))
    for column in gx.cells:
        for cell in column:
            gxx = grid.get_cell(cell.x, cell.y).data.xx
            gxy = grid.get_cell(cell.x, cell.y).data.yx
            cell.data = Vector2(gxx, gxy)
    for column in gy.cells:
        for cell in column:
            gyx = grid.get_cell(cell.x, cell.y).data.xy
            gyy = grid.get_cell(cell.x, cell.y).data.yy
            cell.data = Vector2(gyx, gyy)
    div_x = vector_divergence(gx, dx, x_index, y_index)
    div_y = vector_divergence(gy, dx, x_index, y_index)
    return Vector2(div_x, div_y)


class LinearElasticityPDE:
    def __init__(
            self,
            material_dist: Grid[DataCell[Material]],
            external_force_field: Grid[DataCell[Vector2]],
            total_length: float,
            total_height: float,
            total_time: float,
            dx: float = 0.01,
            dt: float = 0.01
    ):
        self.material_dist = material_dist
        self.external_force_field = external_force_field
        self.stresses: Grid[DataCell[StressTensor]] = Grid(int(total_length / dx), int(total_height / dx), DataCell, Tensor.zero())
        self.strains: Grid[DataCell[Tensor]] = Grid(int(total_length / dx), int(total_height / dx), DataCell, Tensor.zero())
        self.displacements: Grid[DataCell[Vector2]] = Grid(int(total_length / dx), int(total_height / dx), DataCell, Vector2(0, 0))
        self.velocities: Grid[DataCell[Vector2]] = Grid(int(total_length / dx), int(total_height / dx), DataCell, Vector2(0, 0))
        self.total_length = total_length
        self.total_height = total_height
        self.total_time = total_time
        self.current_time = 0
        self.dx = dx
        self.dt = dt

    def get_material(self, i: int, j: int) -> Material:
        return self.material_dist.get_cell(i, j).data

    def get_external_force(self, i: int, j: int):
        return self.external_force_field.get_cell(i, j).data

    def get_u_double_dot(self, i: int, j: int):
        if not self.get_material(i, j).density:
            return Vector2(0, 0)
        return (tensor_divergence(self.stresses, self.dx, i, j) + self.get_external_force(i, j)) * (1/self.get_material(i, j).density)

    def get_u_dot(self, i: int, j: int) -> Vector2:
        return self.velocities.get_cell(i, j).data

    def update_u_dot(self):
        for column in self.velocities.cells:
            for cell in column:
                cell.data += self.get_u_double_dot(cell.x, cell.y) * self.dt

    def update_u(self):
        for column in self.velocities.cells:
            for cell in column:
                cell.data += self.get_u_dot(cell.x, cell.y) * self.dt

    def get_strain(self, i: int, j: int) -> Tensor:
        grad_u = vector_gradient(self.displacements, self.dx, i, j)
        grad_u_transpose = grad_u.transpose
        return 0.5*(grad_u + grad_u_transpose)

    def update_strain(self):
        for column in self.strains.cells:
            for cell in column:
                cell.data = self.get_strain(cell.x, cell.y)

    def get_stress(self, i: int, j: int) -> Tensor:
        strain = self.get_strain(i, j)
        strain_trace = strain.trace
        lame_coefficient_1 = self.get_material(i, j).shear_modulus
        lame_coefficient_2 = self.get_material(i, j).bulk_modulus - (2/3)*lame_coefficient_1
        return 2*lame_coefficient_1*strain + lame_coefficient_2*strain_trace*Tensor.identity()

    def update_stress(self):
        for column in self.strains.cells:
            for cell in column:
                cell.data = self.get_stress(cell.x, cell.y)

    def step(self):
        self.update_u_dot()
        self.update_u()
        self.update_strain()
        self.update_stress()
        self.current_time += self.dt
        return