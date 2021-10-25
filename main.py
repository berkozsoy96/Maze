import cv2
from MazeAndCell import Maze

# Maze dimensions (ncols, nrows)
nx, ny = 40, 40
# Maze entry position
ix, iy = 0, 0

maze = Maze(nx, ny, ix, iy, seed=None)
maze.make_maze()

padding = 30
height = 3000
cell_side_len = height / ny
line_thiccness = 10

maze.write_svg('maze.svg', padding=padding, height=height, line_thickness=line_thiccness)
maze.write_png("maze.png", padding=padding, height=height, line_thickness=line_thiccness)

ratio = 1/3
maze_img = cv2.imread("maze.png")
solution = maze.solve((nx-1, ny-1))
for cell in maze.solution:
    cx = int((padding + (cell.x * cell_side_len) + (cell_side_len/2)))
    cy = int((padding + (cell.y * cell_side_len) + (cell_side_len/2)))
    r = int((cell_side_len - line_thiccness)/2)
    cv2.circle(maze_img, (cx, cy), r, (120, 220, 120), -1)
    cv2.imshow("maze", cv2.resize(maze_img, None, None, ratio, ratio))
    cv2.waitKey()
cv2.destroyAllWindows()
