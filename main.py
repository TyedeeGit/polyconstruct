from polyengine.metricutils import *
from polyengine.diffequations import *
import time

start_time = time.time()

__doc__ = """
Implement pygame graphical interface.
"""

DT = 1
DX = 0.02
LENGTH = 3
HEIGHT = 3
TIME = 1
TOTAL_CELLS = int(LENGTH/DX) * int(HEIGHT/DX)
UPDATE_FREQUENCY = 100
PARALLEL_PROCESS = True
PROCESSES = 36

ranges = []
for j in range(PROCESSES):
    cells_wide = int(LENGTH/DX)
    r = range(int(j*cells_wide/PROCESSES), int((j+1)*cells_wide/PROCESSES))
    ranges.append(r)

DEBUG_X = int(1/DX)
DEBUG_Y = int(1.5/DX)

def run():
    print(f"Simulation parameters: dx={DX}m, region={LENGTH*HEIGHT}m^2, cells={TOTAL_CELLS}, steps={int(TIME/DT)}, dt={DT}s, total-simulation-time={TIME}s")
    print("Setting initial conditions...")

    air = Material('air', 0, 0, 0, 0)
    steel = Material('steel', 8000, 250, 140000, 75000)

    material_distribution = Grid(int(LENGTH/DX), int(HEIGHT/DX), DataCell, air)
    for column in material_distribution.cells:
        for cell in column:
            if int(1/DX) <= cell.y <= int(2/DX):
                cell.data = steel


    external_forces = Grid(int(LENGTH/DX), int(HEIGHT/DX), DataCell, Vector2(0, 0))
    for column in external_forces.cells:
        for cell in column:
            cell.data = material_distribution.get_cell(cell.x, cell.y).data.density * GRAVITY

    for column in external_forces.cells:
        for cell in column:
            if int(1/DX) <= cell.y <= int(2/DX) and (cell.x <= int(1/DX) or cell.x >= int(2/DX)):
                cell.data -= material_distribution.get_cell(cell.x, cell.y).data.density * GRAVITY

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
        print('Computing displacements...')
        computation_start_time = time.time()
        equation.update_u()
        print(f'All {TOTAL_CELLS} displacements computed for step {i+1}/{int(TIME/DT)} in {round(time.time() - computation_start_time, 3)} seconds. Computing velocities...')
        computation_start_time = time.time()
        if PARALLEL_PROCESS:
            with Pool(PROCESSES) as p:
                p.map(equation.update_u_dot, ranges)
        else:
            equation.update_u_dot()
        print(f'All {TOTAL_CELLS} velocities computed for step {i + 1}/{int(TIME / DT)} in {round(time.time() - computation_start_time, 3)} seconds. Computing strains...')
        computation_start_time = time.time()
        if PARALLEL_PROCESS:
            with Pool(PROCESSES) as q:
                q.map(equation.update_strain, ranges)
        else:
            equation.update_strain()
        print(f'All {TOTAL_CELLS} strains computed for step {i+1}/{int(TIME/DT)} in {round(time.time() - computation_start_time, 3)} seconds. Computing stresses...')
        computation_start_time = time.time()
        equation.update_stress()
        step_time = round(time.time() - step_start_time, 3)
        step_times[i] = step_time
        print(f'All {TOTAL_CELLS} stresses computed for step {i+1}/{int(TIME/DT)} in {round(time.time() - computation_start_time, 3)} seconds. Finished simulating step in {step_time} seconds! ({round(time.time() - start_time, 3)} seconds total)')
        equation.current_time += equation.dt

    average_step_time = 0
    for t in step_times:
        average_step_time += t/int(TIME/DT)

    print(f"Finished simulating(dx={DX}m, region={LENGTH*HEIGHT}m^2, cells={TOTAL_CELLS}, steps={int(TIME/DT)}, dt={DT}s, total-simulation-time={TIME}s) in {round(time.time() - start_time, 3)} seconds! Average step time was {round(average_step_time, 3)} seconds.")
    print(f"Stress at {DEBUG_X*DX}m, {DEBUG_Y*DX}m: {equation.stresses.get_cell(DEBUG_X, DEBUG_Y).data}")
    print(f"Strain at {DEBUG_X*DX}m, {DEBUG_Y*DX}m: {equation.strains.get_cell(DEBUG_X, DEBUG_Y).data}")
    print(f"Stress divergence at {DEBUG_X*DX}m, {DEBUG_Y*DX}m: {tensor_divergence(equation.stresses, DX, DEBUG_X, DEBUG_Y)}")
    print(f"Forces near {DEBUG_X*DX}m, {DEBUG_Y*DX}m: {equation.external_force_field.get_neighbors(DEBUG_X, DEBUG_Y)}")
    print(f"Displacements near {DEBUG_X*DX}m, {DEBUG_Y*DX}m: {equation.displacements.get_neighbors(DEBUG_X, DEBUG_Y)}")
    print(f"Vector gradient at {DEBUG_X*DX}m, {DEBUG_Y*DX}m: {vector_gradient(equation.displacements, DX, DEBUG_X, DEBUG_Y)}")
    print(f"Material at {DEBUG_X*DX}m, {DEBUG_Y*DX}m: {equation.get_material(DEBUG_X, DEBUG_Y).material_name}")

if __name__ == '__main__':
    run()
# Graphical interface code goes here
