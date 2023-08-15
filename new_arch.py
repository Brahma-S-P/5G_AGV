import tkinter as tk

# Define cell size and room dimensions
cell_size = 50
room_width = 10  # Number of cells
room_height = 8  # Number of cells

# Initial source area and direction
source_top_left = (0, 0)     # (x, y) top-left corner
source_bottom_right = (1, 1) # (x, y) bottom-right corner
direction = "right"  # Initial direction ("up", "down", "left", "right")

# Create a Tkinter window
root = tk.Tk()
root.title("Robot Control")

canvas = tk.Canvas(root, width=room_width * cell_size, height=room_height * cell_size)
canvas.pack()

# Create grid lines
for x in range(0, room_width * cell_size, cell_size):
    canvas.create_line(x, 0, x, room_height * cell_size)

for y in range(0, room_height * cell_size, cell_size):
    canvas.create_line(0, y, room_width * cell_size, y)

# Function to move the source area
def move_source():
    global source_top_left, source_bottom_right
    source_top_left = (source_top_left[0] + 1, source_top_left[1] + 1)
    source_bottom_right = (source_bottom_right[0] + 1, source_bottom_right[1] + 1)
    canvas.delete("source")
    draw_source_area()

def draw_source_area():
    canvas.create_rectangle(source_top_left[0] * cell_size, source_top_left[1] * cell_size,
                            (source_bottom_right[0] + 1) * cell_size, (source_bottom_right[1] + 1) * cell_size,
                            fill="green", tags="source")
    #draw_robot()
    update_arrow()
    
    
#def draw_robot():
    # Calculate coordinates for the robot
    # x_center = (source_top_left[0] + source_bottom_right[0] + 1) * cell_size / 2
    # y_center = (source_top_left[1] + source_bottom_right[1] + 1) * cell_size / 2


def update_arrow():
    canvas.delete("arrow")
    # Calculate coordinates for the arrow based on robot's direction
    x_center = (source_top_left[0] + source_bottom_right[0] + 1) * cell_size / 2
    y_center = (source_top_left[1] + source_bottom_right[1] + 1) * cell_size / 2

    if direction == "up":
        arrow_coords = [x_center, y_center - cell_size / 4, x_center - cell_size / 4, y_center + cell_size / 4,
                        x_center + cell_size / 4, y_center + cell_size /4]
    elif direction == "down":
        arrow_coords = [x_center, y_center + cell_size / 4, x_center - cell_size / 4, y_center - cell_size / 4,
                        x_center + cell_size / 4, y_center - cell_size / 4]
    elif direction == "left":
        arrow_coords = [x_center - cell_size / 4, y_center, x_center + cell_size / 4, y_center - cell_size / 4,
                        x_center + cell_size / 4, y_center + cell_size / 4]
    elif direction == "right":
        arrow_coords = [x_center + cell_size / 4, y_center, x_center - cell_size / 4, y_center - cell_size / 4,
                        x_center - cell_size / 4, y_center + cell_size / 4]
    canvas.create_polygon(arrow_coords, fill="yellow", outline="black", tags="arrow")

# Function to turn and move the robot
def turn_and_move(new_direction):
    global direction
    clockwise_rotation = {"up": "right", "right": "down", "down": "left", "left": "up"}
    counterclockwise_rotation = {"up": "left", "left": "down", "down": "right", "right": "up"}

    if new_direction == "right":
        direction = clockwise_rotation[direction]
    elif new_direction == "left":
        direction = counterclockwise_rotation[direction]

    canvas.delete("robot")
    update_arrow()

def move_forward():
    global source_top_left, source_bottom_right, direction
    if direction == "up":
        source_top_left = (source_top_left[0], source_top_left[1] - 1)
        source_bottom_right = (source_bottom_right[0], source_bottom_right[1] - 1)
    elif direction == "down":
        source_top_left = (source_top_left[0], source_top_left[1] + 1)
        source_bottom_right = (source_bottom_right[0], source_bottom_right[1]+1)
    elif direction == "left":
        source_top_left = (source_top_left[0] - 1, source_top_left[1])
        source_bottom_right = (source_bottom_right[0] - 1, source_bottom_right[1])
    elif direction == "right":
        source_top_left = (source_top_left[0] + 1, source_top_left[1])
        source_bottom_right = (source_bottom_right[0] + 1, source_bottom_right[1])
    canvas.delete("source")
    draw_source_area()

# Create buttons for direction control
up_button = tk.Button(root, text="Forward", command=lambda: move_forward())
up_button.pack(side="top")
# down_button = tk.Button(root, text="Down", command=lambda: turn_and_move("down"))
# down_button.pack(side="bottom")
left_button = tk.Button(root, text="Left", command=lambda: turn_and_move("left"))
left_button.pack(side="left")
right_button = tk.Button(root, text="Right", command=lambda: turn_and_move("right"))
right_button.pack(side="right")

# Draw initial source area and robot
draw_source_area()

root.mainloop()
