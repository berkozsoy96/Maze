from maze import Maze
import pickle
import os


nx, ny = 30, 30
maze = Maze(nx, ny)
maze.make_maze()
maze.solve((nx - 1, ny - 1))

padding = 15
wall_width = 15
height = 3000

folder = "mazes"
if not os.path.exists(folder):
    os.mkdir(folder)

maze.write_png(folder, padding=padding, height=height, wall_width=wall_width, wall_color=(0, 0, 0), wall_texture_path="wall_piece.png",
               solution_color=(128, 128, 0), solution=True)
maze.write_svg(folder, padding=padding, height=height, wall_width=wall_width, wall_color=(0, 0, 0))
pickle.dump(maze, open(folder + "/maze.pck", "wb"))
