import copy
from typing import TypeVar

class Cell:
    def __init__(self, position):
        self.position = tuple(position)[0:2]
        self.x = self.position[0]
        self.y = self.position[1]
    def __repr__(self):
        return f'Cell({self.position})'

T = TypeVar('T')

class DataCell[T](Cell):
    def __init__(self, position, data):
        super().__init__(position)
        self.data = data
    def __repr__(self):
        return f'DataCell({self.position},{repr(self.data)})'

C = TypeVar('C', bound=Cell)

class Grid[C]:
    """
    A grid of cells. For example:
    Grid(2, 3, DataCell, 'data') gives you a Grid object that looks like
    [\n
    [DataCell((0, 0),'data'), DataCell((1, 0),'data')] \n
    [DataCell((0, 1),'data'), DataCell((1, 1),'data')] \n
    [DataCell((0, 2),'data'), DataCell((1, 2),'data')] \n
    ]
    """
    def __init__(self, columns, rows, cell_cls, *cell_args, **cell_kwargs):
        self.cells = [[Cell([0, 0])] * columns] * rows
        self.cell_cls = cell_cls
        self.cell_args = cell_args
        self.cell_kwargs = cell_kwargs
        self.row_end = rows-1
        self.column_end = columns-1
        for i in range(rows):
            for j in range(columns):
                cell = cell_cls((j, i), *cell_args, *cell_kwargs)
                self.replace_cell(i, j, cell)
    def __str__(self):
        return f'{[[c for c in r] for r in self.cells]}'
    def replace_cell(self, column, row, cell):
        """ Replaces the cell at position (column, row) with a new cell """
        r = copy.copy(self.cells[column])
        r[row] = cell
        self.cells[column] = r
    def get_cell(self, column, row):
        """ Returns the cell at position (column, row) """
        if row not in range(len(self.get_column(0))) or column not in range(len(self.get_row(0))):
            return None
        else:
            return self.cells[row][column]
    def get_row(self, row):
        """ Returns a list of cells at a given row """
        return self.cells[row]
    def get_column(self, column):
        """ Returns a list of cells at a given column """
        return [r[column] for r in self.cells]
    def get_neighbors(self, column, row):
        """ Returns a 3x3 grid of the neighbors of the cell at (column, row) """
        local_grid = Grid(3, 3, self.cell_cls, *self.cell_args, **self.cell_kwargs)
        for i in range(3):
            for j in range(3):
                c = self.get_cell(column+i-1, row+j-1)
                local_grid.replace_cell(j, i, c)
        return local_grid