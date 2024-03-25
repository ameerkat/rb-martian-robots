import argparse

class RobotState:
    def __init__(self, x, y, direction):
        if direction not in ["N", "E", "S", "W"]:
            raise ValueError(f"Invalid direction: {direction}")
        
        self.x = x
        self.y = y
        self.direction = direction

class World:
    # TODO there is a bug where the value we get initially is the upper right coordinate
    # not the width and height of the world. We need to change all bound checks.
    
    def _get_initial_world(width, height):
        # We'll represent the world as a 2D array of booleans. The world representation
        # is slightly larger than the actual world. We include the coordinates the robot
        # can fall off the grid at. True means that a robot was lost at that cell. 
        # False means the cell is in it's default state and a robot can go out of 
        # bounds from it. 
        # In theory we can represent the world with just the perimeter, or even using
        # a dictionary for the invalid coordinates. But for simplicity we'll 
        # represent the whole world since the total size is negligible for a 50x50 grid.

        # Note the coordinate system is flipped. The bottom left is 0, 0 but
        # internally that's the top left of our 2D array. This is a consideration
        # when debugging the world state.
        return [[False for x in range(width + 1)] for y in range(height + 1)]

    def __init__(self, width, height):
        self.width = width
        self.height = height

        if (width <= 0 or width > 50 or height <= 0 or height > 50):
            raise ValueError(f"Invalid world dimensions: {width}, {height}. Min 1, Max 50.")
        self.world = World._get_initial_world(width, height)

    def run_robot(self, x, y, direction, instructions):
        # if (x < 0 or x >= self.width) or (y < 0 or y >= self.height):
        #     raise ValueError(f"Invalid starting position: {x}, {y}")

        # As per the sample data output we'll co-erce the input coordinates
        # to be within the world bounds rather than throwing an error.
        if x < 0:
            x = 0
        elif x >= self.width:
            x = self.width - 1
        
        if y < 0:
            y = 0
        elif y >= self.height:
            y = self.height - 1

        # This is the actual logic to run the robots. This does mutate the world.
        # Because the actions of the robot are dictated by the word, we will
        # simply use the robot as a container for the robot state rather than
        # any logic.
        robot = RobotState(x, y, direction)
        for instruction in instructions:
            out_of_bounds_check_required = False
            out_of_bounds_x = robot.x
            out_of_bounds_y = robot.y

            if instruction == "F":
                if robot.direction == "N":
                    if robot.y == self.height - 1: # The robot is at the top of the world and is about to go out of bounds.
                        out_of_bounds_check_required = True
                        out_of_bounds_y = robot.y + 1
                    else:
                        robot.y += 1
                elif robot.direction == "E":
                    if robot.x == self.width - 1: # The robot is at the right of the world and is about to go out of bounds.
                       out_of_bounds_check_required = True
                       out_of_bounds_x = robot.x + 1
                    else:
                        robot.x += 1
                elif robot.direction == "S":
                    if robot.y == 0: # The robot is at the bottom of the world and is about to go out of bounds.
                       out_of_bounds_check_required = True
                       out_of_bounds_y = robot.y - 1
                    else:
                        robot.y -= 1
                elif robot.direction == "W":
                    if robot.x == 0: # The robot is at the left of the world and is about to go out of bounds.
                        out_of_bounds_check_required = True
                        out_of_bounds_x = robot.x - 1
                    else:
                        robot.x -= 1
                else:
                    raise ValueError(f"Invalid direction: {robot.direction}")
            elif instruction == "L":
                if robot.direction == "N":
                    robot.direction = "W"
                elif robot.direction == "E":
                    robot.direction = "N"
                elif robot.direction == "S":
                    robot.direction = "E"
                elif robot.direction == "W":
                    robot.direction = "S"
                else:
                    raise ValueError(f"Invalid direction: {robot.direction}")
            elif instruction == "R":
                if robot.direction == "N":
                    robot.direction = "E"
                elif robot.direction == "E":
                    robot.direction = "S"
                elif robot.direction == "S":
                    robot.direction = "W"
                elif robot.direction == "W":
                    robot.direction = "N"
                else:
                    raise ValueError(f"Invalid direction: {robot.direction}")
            else:
                raise ValueError(f"Invalid instruction: {instruction}")
            
            if out_of_bounds_check_required:
                # False means the robot can go out of bounds. True means
                # a previous robot was lost here and we ignore the instruction.
                if not self.world[out_of_bounds_y][out_of_bounds_x]:
                    self.world[out_of_bounds_y][out_of_bounds_x] = True
                    # Note when we lose the robot we print the coordinate it was lost at
                    return out_of_bounds_x, out_of_bounds_y, robot.direction, "LOST"
           
        return robot.x, robot.y, robot.direction
    
def run_data(lines):
    result = []

    world_data = lines[0].split()
    if (len(world_data) != 2):
        raise ValueError("Invalid world spec. Must have 2 components width and height.")
    world_width, world_height = map(int, world_data)
    world = World(world_width, world_height)

    # Remove all empty lines from the input data. So we're just left with
    # the robot data in line pairs.
    lines = [line.strip() for line in lines[1:] if line.strip() != ""]
    for i in range(0, len(lines), 2):
        x, y, direction = lines[i].split()
        instructions = lines[i + 1].strip()
        x, y = map(int, [x, y])
        result.append(world.run_robot(x, y, direction, instructions))
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Martian Robots")
    parser.add_argument("file", help="The input file name containing the formatted world and robot data as per the problem statement specfiications.", type=str)
    args = parser.parse_args()

    with open(args.file, "r") as f:
        all_lines = f.readlines()
        result_lines = run_data(all_lines)
        for line in result_lines:
            print(" ".join(map(str, line)))
