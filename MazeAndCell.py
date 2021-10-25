import cv2
import random
import numpy as np


# Create a maze using the depth-first algorithm described at
# https://scipython.com/blog/making-a-maze/
# Christian Hill, April 2017.

class Cell:
    """A cell in the maze.

    A maze "Cell" is a point in the grid which may be surrounded by walls to
    the north, east, south or west.

    """

    # A wall separates a pair of cells in the N-S or W-E directions.
    wall_pairs = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, x, y):
        """Initialize the cell at (x,y). At first it is surrounded by walls."""

        self.x, self.y = x, y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}

    def has_all_walls(self):
        """Does this cell still have all its walls?"""

        return all(self.walls.values())

    def knock_down_wall(self, other, wall):
        """Knock down the wall between cells self and other."""

        self.walls[wall] = False
        other.walls[Cell.wall_pairs[wall]] = False


class Maze:
    """A Maze, represented as a grid of cells."""

    def __init__(self, nx, ny, ix=0, iy=0, seed=None):
        """Initialize the maze grid.
        The maze consists of nx x ny cells and will be constructed starting
        at the cell indexed at (ix, iy).

        """

        self.nx, self.ny = nx, ny
        self.ix, self.iy = ix, iy
        self.maze_map = [[Cell(x, y) for y in range(ny)] for x in range(nx)]
        self.solution = []
        if seed:
            random.seed(seed)

    def cell_at(self, x, y):
        """Return the Cell object at (x,y)."""

        return self.maze_map[x][y]

    def write_svg(self, filename, padding=10, height=500, line_thickness=5):
        """Write an SVG image of the maze to filename."""

        aspect_ratio = self.nx / self.ny

        width = int(height * aspect_ratio)
        # Scaling factors mapping maze coordinates to image coordinates
        scy, scx = height / self.ny, width / self.nx

        def write_wall(ww_f, ww_x1, ww_y1, ww_x2, ww_y2):
            """Write a single wall to the SVG image file handle f."""

            print('<line x1="{}" y1="{}" x2="{}" y2="{}"/>'
                  .format(ww_x1, ww_y1, ww_x2, ww_y2), file=ww_f)

        # Write the SVG image file for maze
        with open(filename, 'w') as f:
            # SVG preamble and styles.
            print('<?xml version="1.0" encoding="utf-8"?>', file=f)
            print('<svg xmlns="http://www.w3.org/2000/svg"', file=f)
            print('    xmlns:xlink="http://www.w3.org/1999/xlink"', file=f)
            print('    width="{:d}" height="{:d}" viewBox="{} {} {} {}">'
                  .format(width + 2 * padding, height + 2 * padding,
                          -padding, -padding, width + 2 * padding, height + 2 * padding),
                  file=f)
            print('<defs>\n<style type="text/css"><![CDATA[', file=f)
            print('line {', file=f)
            print('    stroke: #000000;\n    stroke-linecap: square;', file=f)
            print(f'    stroke-width: {line_thickness};\n}}', file=f)
            print(']]></style>\n</defs>', file=f)
            # Draw the "South" and "East" walls of each cell, if present (these
            # are the "North" and "West" walls of a neighbouring cell in
            # general, of course).
            for x in range(self.nx):
                for y in range(self.ny):
                    if self.cell_at(x, y).walls['S']:
                        x1, y1, x2, y2 = x * scx, (y + 1) * scy, (x + 1) * scx, (y + 1) * scy
                        write_wall(f, x1, y1, x2, y2)
                    if self.cell_at(x, y).walls['E']:
                        x1, y1, x2, y2 = (x + 1) * scx, y * scy, (x + 1) * scx, (y + 1) * scy
                        write_wall(f, x1, y1, x2, y2)
            # Draw the North and West maze border, which won't have been drawn
            # by the procedure above.
            print('<line x1="0" y1="0" x2="{}" y2="0"/>'.format(width), file=f)
            print('<line x1="0" y1="0" x2="0" y2="{}"/>'.format(height), file=f)
            print('</svg>', file=f)

    def write_png(self, filename, padding=10, height=500, line_thickness=5):
        """Write an SVG image of the maze to filename."""

        aspect_ratio = self.nx / self.ny

        width = int(height * aspect_ratio)
        # Scaling factors mapping maze coordinates to image coordinates
        scy, scx = height / self.ny, width / self.nx
        image = np.ones(shape=(height + (2*padding), width + (2*padding), 3), dtype="uint8")*255
        for x in range(self.nx):
            for y in range(self.ny):
                if self.cell_at(x, y).walls['S']:
                    x1, y1 = int(x * scx) + padding, int((y + 1) * scy) + padding
                    x2, y2 = int((x + 1) * scx) + padding, int((y + 1) * scy) + padding
                    cv2.line(image, (x1, y1), (x2, y2), (0, 0, 0), line_thickness)
                if self.cell_at(x, y).walls['E']:
                    x1, y1 = int((x + 1) * scx) + padding, int(y * scy) + padding
                    x2, y2 = int((x + 1) * scx) + padding, int((y + 1) * scy) + padding
                    cv2.line(image, (x1, y1), (x2, y2), (0, 0, 0), line_thickness)

        cv2.line(image, (padding, padding), (width + padding, padding), (0, 0, 0), line_thickness)
        cv2.line(image, (padding, padding), (padding, height + padding), (0, 0, 0), line_thickness)
        cv2.imwrite(filename, image)

    @staticmethod
    def move(cell, direction):
        delta = {
            'W': (-1, 0),
            'E': (1, 0),
            'S': (0, 1),
            'N': (0, -1)
        }
        return cell.x + delta[direction][0], cell.y + delta[direction][1]

    def find_valid_neighbours(self, cell):
        """Return a list of unvisited neighbours to cell."""
        neighbours = []
        for direction in list(cell.walls.keys()):
            x2, y2 = self.move(cell, direction)
            if (0 <= x2 < self.nx) and (0 <= y2 < self.ny):
                neighbour = self.cell_at(x2, y2)
                if neighbour.has_all_walls():
                    neighbours.append((direction, neighbour))
        return neighbours

    def make_maze(self):
        # Total number of cells.
        n = self.nx * self.ny
        cell_stack = []
        current_cell = self.cell_at(self.ix, self.iy)
        # Total number of visited cells during maze construction.
        nv = 1

        while nv < n:
            neighbours = self.find_valid_neighbours(current_cell)

            if not neighbours:
                # We've reached a dead end: backtrack.
                current_cell = cell_stack.pop()
                continue

            # Choose a random neighbouring cell and move to it.
            direction, next_cell = random.choice(neighbours)
            current_cell.knock_down_wall(next_cell, direction)
            cell_stack.append(current_cell)
            current_cell = next_cell
            nv += 1

    def solve(self, destination, start=None, direction=None):

        def check_if_cell_is_destination(cell):
            return cell.x == destination[0] and cell.y == destination[1]

        if start is None:
            start = self.cell_at(self.ix, self.iy)

        if check_if_cell_is_destination(start):
            self.solution.append(start)
            return True

        possible_directions = []
        for k, v in start.walls.items():
            if not v and k != Cell.wall_pairs.get(direction, None):
                possible_directions.append(k)

        self.solution.append(start)
        for possible_direction in possible_directions:
            new_x, new_y = self.move(start, possible_direction)
            new_cell = self.cell_at(new_x, new_y)
            result = self.solve(destination, new_cell, possible_direction)
            if result:
                return result
        self.solution.pop(-1)
        return False
