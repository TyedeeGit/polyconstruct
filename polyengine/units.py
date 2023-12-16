from .metricutils import Unit, DefinedUnit, Measure


# Conversion ratios
METER_TO_FOOT = 0.3048
KILOGRAM_TO_POUND = 0.45359237

# Base metric units
meter = Unit('meters', 'length', symbol='m')
second = Unit('seconds', 'time', symbol='s')
kilogram = Unit('kilograms', 'mass', symbol='kg')

# Derived metric units
newton = DefinedUnit('Newtons', 1*kilogram*meter/(second**2), symbol='N')
pascal = DefinedUnit('Pascals', 1*newton/(meter**2), symbol='Pa')
joule = DefinedUnit('Joules', 1*newton*meter, symbol='J')

# Constants
GRAVITY = 9.80665
gravity = GRAVITY*meter/(second**2)

# Base US units
foot = DefinedUnit('feet', Measure(meter, METER_TO_FOOT), symbol='ft')
inch = DefinedUnit('inches', Measure(foot, 1 / 12), symbol='in')
pound = DefinedUnit('pounds', Measure(kilogram, KILOGRAM_TO_POUND), symbol='lb')

# Derived US units
pound_force = DefinedUnit('pounds-force', (GRAVITY/METER_TO_FOOT) * pound * foot/(second**2), symbol='lbf')
psi = DefinedUnit('pounds/in^2', 1 * pound_force/(inch**2), symbol='psi')
foot_pound = DefinedUnit('foot-pounds', 1 * foot * pound_force, symbol='ft-lbf')
