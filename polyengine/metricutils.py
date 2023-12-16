import math

__doc__ = """
Implements geometric primitives, vectors, and units.
"""

class UnitError(ValueError):
    pass


class Unit:
    def __init__(self, name, dimension, symbol=None, equal_to=()):
        """
        A unit of measurement(ex: foot, meter, inch, psi, Celsius).
        :param name:
        :param dimension:
        :param symbol:
        :param equal_to:
        """
        self.name = name
        self.dimension = dimension
        self.equal_to = list(equal_to)
        self.add_equivalence(1*self)
        if symbol is not None:
            self.symbol = symbol
        else:
            self.symbol = name

    def __eq__(self, other):
        if isinstance(other, Measure):
            return other in self.equal_to
        if self.symbol == other.symbol:
            return True
        for m in self.equal_to:
            if m.unit is other and m.value == 1:
                return True
        return False

    def __repr__(self):
        return f'<Unit[\'{self.name}\', {self.dimension}, \'{self.symbol}\']>'

    def __mul__(self, other):
        """
        Creates a product unit from two other units or a measure from a value and unit(ex: watt*hour -> watt-hour).
        :param other:
        :return:
        """
        if isinstance(other, float) or isinstance(other, int):
            return other*self

        # Check if other is a power
        p = 1
        base_unit = Unit(other.name.split('*')[0], other.dimension.split('*')[0], other.symbol.split('*')[0])
        if other is base_unit ** (len(other.symbol.split('*'))):
            p = len(other.symbol.split('*'))
        if p == 1 or p == -1:
            p = ''
        else:
            p = f'^{p}'
        u = Unit(f'{self.name}*{base_unit.name}{p}', f'{self.dimension}*{base_unit.dimension}{p}', f'{self.symbol}*{base_unit.symbol}{p}')
        return u

    def __rmul__(self, other):
        return Measure(self, other)

    def __truediv__(self, other):
        """
        Creates a rate unit from two other units(ex: meter/second -> m/s).
        :param other:
        :return:
        """
        p = -1
        n1 = other.name
        n2 = other.dimension
        n3 = other.symbol
        base_unit = Unit(other.name.split('*')[0], other.dimension.split('*')[0], other.symbol.split('*')[0])
        base_unit_pow = Unit(other.name.split('^')[0], other.dimension.split('^')[0], other.symbol.split('^')[0])
        # Check for repeated multiplication and simplify to an exponent
        if other is base_unit**(len(other.symbol.split('*'))):
            p = -len(other.symbol.split('*'))
            n1 = f'{base_unit.name}^{p}'
            n2 = f'{base_unit.dimension}^{p}'
            n3 = f'{base_unit.symbol}^{p}'
        if len(other.name.split("^")) > 1:
            if other.name == f'{base_unit_pow.name}^{int(other.name.split("^")[1])}':
                p = -int(other.name.split('^')[1])
                n1 = f'{base_unit_pow.name}^{p}'
                n2 = f'{base_unit_pow.dimension}^{p}'
                n3 = f'{base_unit_pow.symbol}^{p}'
        u = Unit(f'{self.name}*({n1})', f'{self.dimension}*({n2})', f'{self.symbol}*({n3})')
        return u

    def __pow__(self, power):
        """
        Raises a unit to a power(ex: meter^2 -> m^2).
        :param power:
        :return:
        """
        u = self
        for _ in range(power-1):
            u *= self
        p = f'^{power}' if power != 1 else ''
        u.name = f'{self.name}{p}'
        u.dimension = f'{self.dimension}{p}'
        u.symbol = f'{self.symbol}{p}'
        return u if power else 1

    def add_equivalence(self, m):
        """
        Adds an equivalent measure to relate this unit to other units.
        :param m:
        :return:
        """
        self.equal_to.append(m)


class Measure:
    def __init__(self, unit, value):
        """
        A physical measurement, expressed in a unit(ex: 20 feet, 14 meters, 8 Newtons).
        :param unit:
        :param value:
        """
        self.unit = unit
        self.value = value

    def __eq__(self, other):
        return self.unit == other.unit and self.value == other.value

    def __repr__(self):
        return f'<Measure[{self.value} {self.unit.symbol}]>'

    def __add__(self, other):
        pass

    def __mul__(self, other):
        """
        Multiplies two measures to create a new measure with product units, or scale an existing measurement by a number(ex: 5m * 10m -> 50m^2, 3 * 4m -> 12m).
        :param other:
        :return:
        """
        if isinstance(other, float) or isinstance(other, int):
            return Measure(self.unit, self.value*other)
        if isinstance(other, Unit):
            return Measure(self.unit*other, self.value)
        return Measure(self.unit*other.unit, self.value*other.value)

    def __pow__(self, power):
        """
        Raises a measure to a power.
        :param power:
        :return:
        """
        if not isinstance(power, int):
            return ValueError("Units can only be raised to integer powers!")
        m = self
        for _ in range(power - 1):
            m *= self
        return m if power else 1

    def __truediv__(self, other):
        """
        Divides two measures to create a new measure with rate units, or divide an existing measurement by a number(ex: 20m/5s -> 4m/s, 15ft/3 -> 5ft).
        :param other:
        :return:
        """
        if isinstance(other, int) or isinstance(other, float):
            return Measure(self.unit, self.value/other)
        if isinstance(other, Unit):
            return Measure(self.unit/other, self.value)
        if other.unit.dimension == self.unit.dimension:
            for m in other.unit.equal_to:
                if m.unit is self.unit:
                    return (self.value/other.value)*m.value
        return Measure(self.unit/other.unit, self.value/other.value)

    def convert(self, target_unit):
        """
        Converts the measure into another unit(ex: 3kg -> 3000g, 24in -> 2ft). The target unit must have the same dimensions.
        :param target_unit:
        :return:
        """
        if target_unit.dimension != self.unit.dimension:
            raise UnitError(f"Expected target unit with dimension of {self.unit.dimension}, got unit with dimension of {target_unit.dimension}.")
        if target_unit is self.unit:
            return self
        for m in self.unit.equal_to:
            if m.unit.name == target_unit.name:
                return self.value * m.value * m.unit
        raise UnitError("No unit conversion found.")

    def __round__(self, n=None):
        """
        Rounds the value of the measurement to n digits.
        :param n:
        :return:
        """
        return Measure(self.unit, round(self.value, n))


class DefinedUnit(Unit):
    def __init__(self, name, *measures, symbol=None):
        """
        A unit defined in terms of another unit(ex: foot = 0.3048 * meter).
        :param name:
        :param measures:
        :param symbol:
        """
        # Add equivalences for easy conversion
        for m in measures:
            m.unit.add_equivalence(Measure(self, 1/m.value))
        super().__init__(name, measures[0].unit.dimension, symbol=symbol, equal_to=measures)

    def __mul__(self, other):
        u = super().__mul__(other)
        if isinstance(other, int) or isinstance(other, float):
            return u
        for m1 in self.equal_to:
            for m2 in other.equal_to:
                if not (isinstance(m1.unit, DefinedUnit) or isinstance(m2.unit, DefinedUnit)):
                    u.add_equivalence(m1*m2)
        return u

    def __pow__(self, power):
        u = super().__pow__(power)
        for m in self.equal_to:
            if m.unit != self:
                u.add_equivalence(m**power)
        return u


# Angle units
radian = Unit('radian', 'angle', symbol='rad')
turn = DefinedUnit('turn', radian*math.tau, symbol='turn')
degree = DefinedUnit('degree', turn*(1/360), radian*math.tau*(1/360), symbol='deg')


class Vector2:
    def __init__(self, x, y):
        """
        A 2D vector.
        :param x:
        :param y:
        """
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Vector2[{self.x}, {self.y}]'

    def __add__(self, other):
        """
        Add two vectors component-wise.
        :param other:
        :return:
        """
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """
        Subtract two vectors component-wise.
        :param other:
        :return:
        """
        return self + -other

    def __neg__(self):
        """
        Scale a vector by -1.
        :return:
        """
        return (-1)*self

    def __mul__(self, other):
        """
        Scale a vector component-wise, or take the dot product of two vectors.
        :param other:
        :return:
        """
        if isinstance(other, Vector2):
            return self.x * other.x + self.y * other.y
        if isinstance(other, float) or isinstance(other, int):
            return Vector2(self.x * other, self.y * other)
        raise TypeError(f'Multiplication not supported for {other}.')

    def __rmul__(self, other):
        return self * other

    def __abs__(self):
        """
        Take the norm of a vector.
        :return:
        """
        return math.sqrt(self * self)


def get_distance(pos1: Vector2, pos2: Vector2) -> float:
    """
    Gets the distance between two points.
    :param pos1:
    :param pos2:
    :return:
    """
    return abs(pos2-pos1)


def get_angle(pos1: Vector2, pos2: Vector2, center: Vector2 = Vector2(0, 0), unit=radian) -> float:
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
        Wraps an inequality.
        Inequality can be ==, >, >=, <=, <.
        :param constant:
        :param inequality:
        """
        if inequality not in {'==', '>', '>=', '<=', '<'}:
            raise ValueError('Invalid inequality.')
        self.constant = constant
        self.inequality = inequality
        self.strict = '=' in inequality

    def __call__(self, value: float) -> bool:
        """
        Tests if a value satisfies the inequality.
        :param value:
        :return:
        """
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
    def in_set(self, point: Vector2) -> bool:
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

    def in_set(self, point: Vector2) -> bool:
        """
        Checks if a point is in the defined region or set.
        :param point:
        :return:
        """
        c1, c2, c0 = self.coefficients
        return self.condition(c1 * point.x + c2 * point.y + c0)

    @classmethod
    def from_slope_intercept(cls, slope: float, intercept: float, inequality: str):
        """
        Constructs the defining line from slope-intercept form.
        :param slope:
        :param intercept:
        :param inequality:
        :return:
        """
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
        # Unpack coefficients
        self_c1, self_c2, self_c3 = self.coefficients
        other_c1, other_c2, other_c3 = other.coefficients
        # Test if coefficients are both zero or non-zero
        if not all((
                (self_c1 and other_c1 or self_c1 == other_c1 == 0),
                (self_c2 and other_c2 or self_c2 == other_c2 == 0),
                (self_c3 and other_c3 or self_c3 == other_c3 == 0),
        )):
            return False
        # Test if the ratios of the coefficients are the same
        elif 0 in {self_c1, self_c2}:
            self_nonzero, other_nonzero = (self_c1, other_c1) if self_c1 else (self_c2, other_c2)
            return self_c3/self_nonzero == other_c3/other_nonzero
        else:
            return self_c3/self_c1 == other_c3/other_c1 and self_c3/self_c2 == other_c3/other_c2 and self_c1/self_c2 == other_c1/other_c2


class Segment(Line):
    def __init__(self, p1: Vector2, p2: Vector2):
        """
        A line segment between two points.
        :param p1:
        :param p2:
        """
        if p1 == p2:
            raise ValueError('Segment must consist of distinct points.')
        x0, y0 = p1.x, p1.y
        x1, y1 = p2.x, p2.y
        # Calculate coefficients
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

    def in_set(self, point: Vector2) -> bool:
        inequalities: tuple[tuple[str, str], tuple[str, str]] = ((), ())
        # Ensures the inequalities are in the right order, in case the points were given in the wrong order
        match [self.p2.x > self.p1.x, self.p2.y > self.p1.y]:
            case [True, True]:
                inequalities = (('>=', '<='), ('>=', '<='))
            case [True, False]:
                inequalities = (('>=', '<='), ('<=', '>='))
            case [False, True]:
                inequalities = (('<=', '>='), ('>=', '<='))
            case [False, False]:
                inequalities = (('<=', '>='), ('<=', '>='))
        # Conditions check if the point is within a bounding box formed by the segment endpoints, but the inequalities must match the order of the endpoints
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
        """
        A directed line.
        :param c1:
        :param c2:
        :param c3:
        :param direction:
        """
        if direction not in {'+', '-'}:
            raise ValueError("Invalid ray direction. Options are '+' or '-'")
        self.direction = direction
        self.dir_region = Region(-c2, c1, c3, '>=' if direction == '+' else '<=')
        super().__init__(c1, c2, c3)

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.direction == other.direction

    def in_set(self, point: Vector2) -> bool:
        return super().in_set(point) and point in self.dir_region
