from polyengine.metricutils import *
from polyengine.diffequations import *
import time

start_time = time.time()

__doc__ = """
Implement pygame graphical interface.
"""

DT = 0.01
DX = 0.1
LENGTH = 3
HEIGHT = 3
TIME = 1
TOTAL_CELLS = int(LENGTH/DX) * int(HEIGHT/DX)
GRAVITY = Vector2(0, -9.8)
UPDATE_FREQUENCY = 100
GIVE_UPDATES = False

print(f"Simulation parameters: dx={DX}m, region={LENGTH*HEIGHT}m^2, cells={TOTAL_CELLS}, steps={int(TIME/DT)}, dt={DT}s, total-simulation-time={TIME}s")
print("Setting initial conditions...")

air = Material('air', 0, 0, 0, 0)
steel = Material('steel', 8000, 250, 140000, 75000)

material_distribution = Grid(int(LENGTH/DX), int(HEIGHT/DX), DataCell, air)
for column in material_distribution.cells:
    for cell in column:
        if 1/DX <= cell.y/DX <= 2/DX:
            cell.data = steel

external_forces = Grid(int(LENGTH/DX), int(HEIGHT/DX), DataCell, Vector2(0, 0))
for column in external_forces.cells:
    for cell in column:
        if 1/DX <= cell.y/DX <= 2/DX:
            cell.data = material_distribution.cells[cell.x][cell.y].data.density * GRAVITY

equation = LinearElasticityPDE(
    material_distribution,
    external_forces,
    LENGTH,
    HEIGHT,
    TIME,
    dx=DX,
    dt=DT
)

print(f"Initial conditions set in {round(time.time() - start_time, 3)} seconds, starting simulation...")
step_times = [0]*int(TIME/DT)
for i in range(int(TIME/DT)):
    step_start_time = time.time()
    print(f'Step {i+1}/{int(TIME/DT)}(simulation-time={round((i+1)*DT, 3)}s):')
    print('Computing velocities...')
    cells_counted = 0
    computation_start_time = time.time()
    for column in equation.velocities.cells:
        for cell in column:
            if not cells_counted % UPDATE_FREQUENCY and GIVE_UPDATES:
                print(f'Velocities {cells_counted}/{TOTAL_CELLS} computed.')
            cells_counted += 1
            cell.data += equation.get_u_double_dot(cell.x, cell.y) * equation.dt
    print(f'All {TOTAL_CELLS} velocities computed for step {i+1}/{int(TIME/DT)}. Computing displacements...')
    cells_counted = 0
    computation_start_time = time.time()
    for column in equation.velocities.cells:
        for cell in column:
            if not cells_counted % UPDATE_FREQUENCY and GIVE_UPDATES:
                print(f'Displacements {cells_counted}/{TOTAL_CELLS} computed.')
            cells_counted += 1
            cell.data += equation.get_u_dot(cell.x, cell.y) * equation.dt
    print(f'All {TOTAL_CELLS} displacements computed for step {i+1}/{int(TIME/DT)}. Computing strains...')
    cells_counted = 0
    computation_start_time = time.time()
    for column in equation.strains.cells:
        for cell in column:
            if not cells_counted % UPDATE_FREQUENCY and GIVE_UPDATES:
                print(f'Strains {cells_counted}/{TOTAL_CELLS} computed.')
            cells_counted += 1
            cell.data = equation.get_strain(cell.x, cell.y)
    print(f'All {TOTAL_CELLS} strains computed for step {i+1}/{int(TIME/DT)}. Computing stresses...')
    cells_counted = 0
    computation_start_time = time.time()
    for column in equation.strains.cells:
        for cell in column:
            if not cells_counted % UPDATE_FREQUENCY and GIVE_UPDATES:
                print(f'Stresses {cells_counted}/{TOTAL_CELLS} computed.')
            cells_counted += 1
            cell.data = equation.get_stress(cell.x, cell.y)
    step_time = round(time.time() - step_start_time, 3)
    step_times[i] = step_time
    print(f'All {TOTAL_CELLS} stresses computed for step {i+1}/{int(TIME/DT)}. Finished simulating step in {step_time} seconds({round(time.time() - start_time, 3)} seconds total)!')
    equation.current_time += equation.dt

average_step_time = 0
for t in step_times:
    average_step_time += t/int(TIME/DT)

print(f"Finished simulating(dx={DX}m, region={LENGTH*HEIGHT}m^2, cells={TOTAL_CELLS}, steps={int(TIME/DT)}, dt={DT}s, total-simulation-time={TIME}s) in {round(time.time() - start_time, 3)} seconds. Average step time was {round(average_step_time, 3)}")

# Graphical interface code goes here
