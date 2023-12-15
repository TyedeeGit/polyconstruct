import math
import copy


class Unit:
    def __init__(self, name, dimension, symbol=None, equal_to=()):
        self.name = name
        self.dimension = dimension
        self.equal_to = list(equal_to)
        if symbol is not None:
            self.symbol = symbol
        else:
            self.symbol = name

    def __eq__(self, other):
        return other in [m.unit for m in self.equal_to]

    def __repr__(self):
        return self.symbol

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return other*self
        p = 1
        base_unit = Unit(other.name.split('*')[0], other.dimension.split('*')[0], other.symbol.split('*')[0])
        if other == base_unit ** (len(other.symbol.split('*'))):
            p = -len(other.symbol.split('*'))
        if p == 1 or p == -1:
            p = ''
        else:
            p = f'^{p}'
        u = Unit(f'{self.name}*{base_unit.name}{p}', f'{self.dimension}*{base_unit.dimension}{p}', f'{self.symbol}*{base_unit.symbol}{p}')
        u.equal_to.append(copy.deepcopy(u).__dict__)
        return u

    def __rmul__(self, other):
        return Measure(self, other)

    def __truediv__(self, other):
        p = -1
        base_unit = Unit(other.name.split('*')[0], other.dimension.split('*')[0], other.symbol.split('*')[0])
        if other is base_unit**(len(other.symbol.split('*'))):
            p = -len(other.symbol.split('*'))
        u = Unit(f'{self.name}*({base_unit.name}^{p})', f'{self.dimension}*({base_unit.dimension}^{p})', f'{self.symbol}*({base_unit.symbol}^{p})')
        u.equal_to.append(copy.deepcopy(u).__dict__)
        return u

    def __pow__(self, power):
        u = self
        for _ in range(power-1):
            u *= self
        return u if power else 1

    def add_equivalence(self, m):
        self.equal_to.append(m)


class Measure:
    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    def __eq__(self, other):
        return self.unit == other.unit and self.value == other.value

    def __repr__(self):
        return f'{self.value} {self.unit.symbol}'

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Measure(self.unit, self.value*other)
        return Measure(self.unit*other.unit, self.value*other.value)

    def __truediv__(self, other):
        if isinstance(other, Unit):
            return Measure(self.unit/other, self.value)
        return Measure(self.unit/other.unit, self.value/other.value)

    def convert(self, target_unit):
        if target_unit is self.unit:
            return self
        for m in self.unit.equal_to:
            if m.unit.name == target_unit.name:
                return self.value * m.value * m.unit
        raise ValueError("No unit conversion found.")

    def __round__(self, n=None):
        return Measure(self.unit, round(self.value, n))


class DefinedUnit(Unit):
    def __init__(self, name, *measures, symbol=None):
        for m in measures:
            m.unit.add_equivalence(Measure(self, 1/m.value))
        super().__init__(name, measures[0].unit.dimension, symbol=symbol, equal_to=measures)


# Angle units
radian = Unit('radian', 'angle', symbol='rad')
turn = DefinedUnit('turn', radian*math.tau, symbol='turn')
degree = DefinedUnit('degree', turn*(1/360), radian*math.tau*(1/360), symbol='deg')

# Base units
meter = Unit('meter', 'length', symbol='m')
second = Unit('second', 'time', symbol='s')
kilogram = Unit('kilogram', 'mass', symbol='kg')

# Derived metric units
newton = kilogram*meter/(second**2)
newton.name = 'Newton'
newton.symbol = 'N'

pascal = newton/(meter**2)
pascal.name = 'Pascal'
pascal.symbol = 'Pa'


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Vector[{self.x}, {self.y}]'

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return self + -other

    def __neg__(self):
        return (-1)*self

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        if isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other)
        raise TypeError(f'Multiplication not supported for {other}.')

    def __rmul__(self, other):
        return self * other

    def __abs__(self):
        return math.sqrt(self * self)


def get_distance(pos1: Vector, pos2: Vector) -> float:
    """
    Gets the distance between two points.
    :param pos1:
    :param pos2:
    :return:
    """
    return abs(pos2-pos1)


def get_angle(pos1: Vector, pos2: Vector, center: Vector = Vector(0, 0), unit=radian) -> float:
    """
    Gets the angle two points make when connected to a center point.
    Unit options are rad, deg, and turns.
    :param pos1:
    :param pos2:
    :param center:
    :param unit:
    :return:
    """
    vector1 = pos1-center
    vector2 = pos2-center
    norm_prod = abs(vector1)*abs(vector2)
    dot_prod = vector1 * vector2
    angle = math.acos(dot_prod/norm_prod) * radian
    return angle.convert(unit)


class Condition:
    def __init__(self, constant: float, inequality: str):
        """
        An inequality wrapper.
        :param constant:
        :param inequality:
        """
        if inequality not in {'==', '>', '>=', '<=', '<'}:
            raise ValueError('Invalid inequality.')
        self.constant = constant
        self.inequality = inequality
        self.strict = '=' in inequality

    def __call__(self, value: float) -> bool:
        match self.inequality:
            case '==':
                return value == self.constant
            case '>=':
                return value >= self.constant
            case '<=':
                return value <= self.constant
            case '>':
                return value > self.constant
            case '<':
                return value < self.constant


class Primitive(set):
    """
    Root of all geometric objects.
    """
    def in_set(self, point: Vector) -> bool:
        """
        Returns true if point is inside primitive.
        :return:
        """
        return False

    def __contains__(self, item):
        return self.in_set(item)


class Region(Primitive):
    def __init__(self, c1: float, c2: float, c3: float, inequality: str):
        """
        A region defined by the line c1*x + c2*y + c3 == 0
        :param c1:
        :param c2:
        :param c3:
        :param inequality:
        """
        if c1 == c2 == 0:
            raise ValueError('Invalid line. c1 and c2 cannot be both 0.')
        self.coefficients = (c1, c2, c3)
        self.condition = Condition(0, inequality)
        super().__init__()

    def in_set(self, point: Vector) -> bool:
        c1, c2, c0 = self.coefficients
        return self.condition(c1 * point.x + c2 * point.y + c0)

    @classmethod
    def from_slope_intercept(cls, slope: float, intercept: float, inequality: str):
        return cls(slope, -1, intercept, inequality)


class Line(Region):
    def __init__(self, c1: float, c2: float, c3: float):
        """
        The line defined by c1*x + c2*y + c3 == 0
        :param c1:
        :param c2:
        :param c3:
        """
        super().__init__(c1, c2, c3, '==')

    def __eq__(self, other) -> bool:
        self_c1, self_c2, self_c3 = self.coefficients
        other_c1, other_c2, other_c3 = other.coefficients
        if not all((
                (self_c1 and other_c1 or self_c1 == other_c1 == 0),
                (self_c2 and other_c2 or self_c2 == other_c2 == 0),
                (self_c3 and other_c3 or self_c3 == other_c3 == 0),
        )):
            return False
        elif 0 in {self_c1, self_c2}:
            self_nonzero, other_nonzero = (self_c1, other_c1) if self_c1 else (self_c2, other_c2)
            return self_c3/self_nonzero == other_c3/other_nonzero
        else:
            return self_c3/self_c1 == other_c3/other_c1 and self_c3/self_c2 == other_c3/other_c2 and self_c1/self_c2 == other_c1/other_c2


class Segment(Line):
    def __init__(self, p1: Vector, p2: Vector):
        """
        A line segment between two points.
        :param p1:
        :param p2:
        """
        if p1 == p2:
            raise ValueError('Segment must consist of distinct points.')
        x0, y0 = p1.x, p1.y
        x1, y1 = p2.x, p2.y
        c1 = y1-y0
        c2 = x0-x1
        c3 = y0*x1+x1*y1-x0*y1-y1*x1
        self.p1 = p1
        self.p2 = p2
        super().__init__(c1, c2, c3)

    def __eq__(self, other) -> bool:
        return self.p1 == other.p1 and self.p2 == other.p2 or self.p1 == other.p2 and self.p2 == other.p1

    def extended(self) -> Line:
        """
        Returns the line that encompasses the segment.
        :return:
        """
        return Line(*self.coefficients)

    def in_set(self, point: Vector) -> bool:
        inequalities: tuple[tuple[str, str], tuple[str, str]] = ((), ())
        match [self.p2.x > self.p1.x, self.p2.y > self.p1.y]:
            case [True, True]:
                inequalities = (('>=', '<='), ('>=', '<='))
            case [True, False]:
                inequalities = (('>=', '<='), ('<=', '>='))
            case [False, True]:
                inequalities = (('<=', '>='), ('>=', '<='))
            case [False, False]:
                inequalities = (('<=', '>='), ('<=', '>='))
        condition_x0 = Condition(self.p1.x, inequalities[0][0])
        condition_y0 = Condition(self.p1.y, inequalities[1][0])
        condition_x1 = Condition(self.p2.x, inequalities[0][1])
        condition_y1 = Condition(self.p2.y, inequalities[1][1])
        return all((
            super().in_set(point),
            condition_x0(point.x),
            condition_x1(point.x),
            condition_y0(point.y),
            condition_y1(point.y),
        ))


class Ray(Line):
    def __init__(self, c1: float, c2: float, c3: float, direction: str = '+'):
        if direction not in {'+', '-'}:
            raise ValueError("Invalid ray direction. Options are '+' or '-'")
        self.direction = direction
        self.dir_region = Region(-c2, c1, c3, '>=' if direction == '+' else '<=')
        super().__init__(c1, c2, c3)

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.direction == other.direction

    def in_set(self, point: Vector) -> bool:
        return super().in_set(point) and point in self.dir_region


