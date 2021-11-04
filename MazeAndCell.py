# Create a maze using the depth-first algorithm described at
# https://scipython.com/blog/making-a-maze/
# Christian Hill, April 2017.

import os
import cv2
import random
import numpy as np


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

    def __init__(self, nx, ny, ix=0, iy=0):
        """
        Initialize the maze grid.
        The maze consists of nx x ny cells and will be constructed starting
        at the cell indexed at (ix, iy).
        """

        self.nx, self.ny = nx, ny
        self.ix, self.iy = ix, iy
        self.last_x, self.last_y = self.nx - 1, self.ny - 1
        self.maze_map = [[Cell(x, y) for y in range(ny)] for x in range(nx)]
        self.solution = []

    def cell_at(self, x, y):
        """Return the Cell object at (x,y)."""

        return self.maze_map[x][y]

    def write_svg(self, foldername, padding=10, height=2000, wall_width=5, wall_color=(0, 0, 0)):
        """Write an SVG image of the maze to filename."""

        aspect_ratio = self.nx / self.ny
        width = int(height * aspect_ratio)
        # Scaling factors mapping maze coordinates to image coordinates
        scy, scx = height / self.ny, width / self.nx
        hex_color = "".join([f'{c:02x}' for c in wall_color])

        def write_wall(ww_f, ww_x1, ww_y1, ww_x2, ww_y2):
            """Write a single wall to the SVG image file handle f."""

            print('<line x1="{}" y1="{}" x2="{}" y2="{}"/>'
                  .format(ww_x1, ww_y1, ww_x2, ww_y2), file=ww_f)

        # Write the SVG image file for maze
        with open(os.path.join(foldername, "maze.svg"), 'w') as f:
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
            print(f'    stroke: #{hex_color};\n    stroke-linecap: square;', file=f)
            print(f'    stroke-width: {wall_width};\n}}', file=f)
            print(']]></style>\n</defs>', file=f)
            # Draw the "South" and "East" walls of each cell, if present (these
            # are the "North" and "West" walls of a neighbouring cell in
            # general, of course).
            for x in range(self.nx):
                for y in range(self.ny):
                    if self.cell_at(x, y).walls['S'] and not (y == self.ny - 1 and x == self.nx - 1):
                        x1, y1, x2, y2 = x * scx, (y + 1) * scy, (x + 1) * scx, (y + 1) * scy
                        write_wall(f, x1, y1, x2, y2)
                    if self.cell_at(x, y).walls['E']:
                        x1, y1, x2, y2 = (x + 1) * scx, y * scy, (x + 1) * scx, (y + 1) * scy
                        write_wall(f, x1, y1, x2, y2)
            # Draw the North and West maze border, which won't have been drawn
            # by the procedure above.
            print(f'<line x1="{scx}" y1="0" x2="{width}" y2="0"/>', file=f)
            print(f'<line x1="0" y1="0" x2="0" y2="{height}"/>', file=f)
            print('</svg>', file=f)

    def write_png(self, foldername, padding=10, height=2000, wall_width=5, wall_color=(0, 0, 0), wall_texture_path="",
                  solution_color=(128, 128, 0), solution=False):
        """Write an PNG image of the maze to filename."""

        def get_wall_points(maze_cell, direction):
            x1, y1 = padding + (maze_cell.x * scx), padding + (maze_cell.y * scy)
            x2, y2 = (maze_cell.x * scx) + padding, (maze_cell.y * scy) + padding
            if direction == "W":
                y2 += scy
            elif direction == "N":
                x2 += scx
            elif direction == "S":
                y1 += scy
                y2 += scy
                x2 += scx
            elif direction == "E":
                x1 += scx
                y2 += scy
                x2 += scx
            return np.array([x1, y1]).astype("int32"), np.array([x2, y2]).astype("int32")

        def draw_solution():
            radius = int((min(scy, scx) - wall_width) / 2)
            for cell in self.solution:
                cx, cy = int(padding + scx / 2 + (cell.x * scx)), int(padding + scy / 2 + (cell.y * scy))
                cv2.circle(maze, (cx, cy), radius, solution_color, -1)

        aspect_ratio = self.nx / self.ny
        width = int(height * aspect_ratio)
        maze = np.ones(shape=(height, width, 3), dtype=np.uint8) * 255
        # Scaling factors mapping maze coordinates to image coordinates
        scy, scx = (height-(2*padding)) / self.ny, (width-(2*padding)) / self.nx
        if wall_texture_path != "":
            wall_width = wall_width if wall_width % 2 == 0 else wall_width - 1
            wall_texture = cv2.imread(wall_texture_path)
            wall_texture = cv2.resize(wall_texture, (int(scx), wall_width))
            wall_texture_vertical = cv2.rotate(wall_texture, cv2.ROTATE_90_CLOCKWISE)

        for ir, maze_row in enumerate(self.maze_map):
            for ic, cell in enumerate(maze_row):
                for k, v in cell.walls.items():
                    if v:
                        if (cell.x == 0 and cell.y == 0 and k == "N") or \
                                (cell.x == self.nx-1 and cell.y == self.ny-1 and k == "S"):
                            continue
                        pt1, pt2 = get_wall_points(cell, k)
                        if wall_texture_path != "":
                            if pt1[0] - pt2[0] == 0:
                                new_pt1 = (pt1[0]-int(wall_width/2), pt1[1])
                                new_pt2 = (pt2[0]+int(wall_width/2), pt2[1])
                                maze[new_pt1[1]:new_pt2[1], new_pt1[0]:new_pt2[0]] = wall_texture_vertical
                            else:
                                new_pt1 = (pt1[0], pt1[1] - int(wall_width / 2))
                                new_pt2 = (pt2[0], pt2[1] + int(wall_width / 2))
                                maze[new_pt1[1]:new_pt2[1], new_pt1[0]:new_pt2[0]] = wall_texture
                        else:
                            cv2.line(maze, pt1, pt2, color=wall_color, thickness=wall_width)
        cv2.imwrite(os.path.join(foldername, "maze.png"), maze)
        if solution:
            if len(self.solution) != 0:
                draw_solution()
                cv2.imwrite(os.path.join(foldername, "solution.png"), maze)
            else:
                print("No solution found")

    @staticmethod
    def move(cell, direction):
        delta = {'W': (-1, 0),
                 'E': (1, 0),
                 'S': (0, 1),
                 'N': (0, -1)}
        return cell.x + delta[direction][0], cell.y + delta[direction][1]

    def find_valid_neighbours(self, cell):
        """Return a list of unvisited neighbours to cell."""

        directions = ['W', 'E', 'S', 'N']
        neighbours = []
        for direction in directions:
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

    def solve(self, destination, start=None, come_from=None):

        def check_cell_is_destination(cell):
            return cell.x == destination[0] and cell.y == destination[1]

        start_cell = self.cell_at(self.ix, self.iy) if start is None else self.cell_at(start[0], start[1])

        if check_cell_is_destination(start_cell):
            self.solution.append(start_cell)
            return True

        possible_directions = []
        for k, v in start_cell.walls.items():
            if not v and k != start_cell.wall_pairs.get(come_from, None):
                possible_directions.append(k)

        if len(possible_directions) == 0:
            return False

        self.solution.append(start_cell)

        for possible_direction in possible_directions:
            new_coor = self.move(start_cell, possible_direction)
            result = self.solve(destination, new_coor, possible_direction)
            if result:
                return True
        self.solution.pop(-1)
        return False
