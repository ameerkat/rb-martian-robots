import argparse
import json
import base64
import urllib.parse

class RobotState:
    def __init__(self, x, y, direction):
        if direction not in ["N", "E", "S", "W"]:
            raise ValueError(f"Invalid direction: {direction}")
        
        self.x = x
        self.y = y
        self.direction = direction


class World:
    def _get_initial_world(width, height):
        """
        Returns a 2D array representing the world for a world of width x height.

        We represent the world as a 2D array of booleans. These can be expanded
        later if we need additional state for locations in the world. For now
        state is simply
        
        True: A robot was lost at this cell.
        False: A robot can go out of bounds from this cell. This is the initial state.
        
        In theory we can represent the world with just the perimeter, or even using
        a dictionary for the invalid coordinates. But for simplicity we'll 
        represent the whole world since the total data usage is negligible for a 50x50 grid.
        
        Also note the coordinate system is flipped, both in that y coordinate
        is passed first to an array, and that the y coordinate is flipped as 0
        is the bottom. This is a consideration when printing or debugging the world state.
        """
        return [[False for x in range(width)] for y in range(height)]

    def __init__(self, top_x_coordinate, top_y_coorindate):
        self.width = top_x_coordinate + 1
        self.height = top_y_coorindate + 1

        if (self.width <= 0 or self.width > 51 or self.height <= 0 or self.height > 51):
            raise ValueError(f"Invalid world dimensions: {self.width}, {self.height}. Min 1, Max 50.")
        self.world = World._get_initial_world(self.width, self.height)

    def run_robot(self, x, y, direction, instructions):
        """
        Runs a robot from a starting position and direction with a set of instructions.
        """

        if (x < 0 or x >= self.width) or (y < 0 or y >= self.height):
            raise ValueError(f"Invalid starting position: {x}, {y}")

        # TODO this function is getting to the length where I would split it.
        
        # This is the actual logic to run the robots. This does mutate the world.
        # Because the actions of the robot are dictated by the world, and robots
        # can mutate the world through falling off, we will simply use the robot 
        # as a container for the robot state rather than any logic.
        robot = RobotState(x, y, direction)
        for instruction in instructions:
            out_of_bounds_check_required = False

            if instruction == "F":
                if robot.direction == "N":
                    if robot.y == self.height - 1: # The robot is at the top of the world and is about to go out of bounds.
                        out_of_bounds_check_required = True
                    else:
                        robot.y += 1
                elif robot.direction == "E":
                    if robot.x == self.width - 1: # The robot is at the right of the world and is about to go out of bounds.
                       out_of_bounds_check_required = True
                    else:
                        robot.x += 1
                elif robot.direction == "S":
                    if robot.y == 0: # The robot is at the bottom of the world and is about to go out of bounds.
                       out_of_bounds_check_required = True
                    else:
                        robot.y -= 1
                elif robot.direction == "W":
                    if robot.x == 0: # The robot is at the left of the world and is about to go out of bounds.
                        out_of_bounds_check_required = True
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
                if not self.world[robot.y][robot.x]:
                    self.world[robot.y][robot.x] = True
                    return robot.x, robot.y, robot.direction, "LOST"
        
        return robot.x, robot.y, robot.direction


def run_data(lines):
    """
    Takes a list of lines and runs the simulation, returning a list of result states.
    """

    result = []

    world_data = lines[0].split()
    if (len(world_data) != 2):
        raise ValueError("Invalid world spec. Must have 2 components width and height.")
    top_x_coordinate, top_y_coordinate = map(int, world_data)
    world = World(top_x_coordinate, top_y_coordinate)

    # Remove all empty lines from the input data. So we're just left with
    # the robot data in line pairs.
    lines = [line.strip() for line in lines[1:] if line.strip() != ""]
    for i in range(0, len(lines), 2):
        x, y, direction = lines[i].split()
        if (i + 1 >= len(lines)):
            raise ValueError("Invalid robot data. Missing instructions.")
        instructions = lines[i + 1].strip()
        x, y = map(int, [x, y])
        result.append(world.run_robot(x, y, direction, instructions))
    
    return result


def lambda_handler(event, context):
    print(json.dumps(event))
    if event["requestContext"]["http"]["method"] == "GET":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": """
<form method="POST">
    <textarea name="data"></textarea>
    <button type="submit">Submit</button>
</form>
        """
        }
    elif event["requestContext"]["http"]["method"] == "POST":
        if event["isBase64Encoded"]: # base 64 decode body if necessary
            event["body"] = base64.b64decode(event["body"]).decode("utf-8")
        data = urllib.parse.unquote_plus(event["body"][5:])
        print(data)
        lines = data.split("\n")
        try:
            result_lines = run_data(lines)
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/plain"
                },
                "body": "\n".join(" ".join(map(str, line)) for line in result_lines)
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "text/plain"
                },
                "body": str(e)
            }


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Martian Robots")
    parser.add_argument("file", help="The input file name containing the formatted world and robot data as per the problem statement specfiications.", type=str)
    args = parser.parse_args()

    with open(args.file, "r") as f:
        all_lines = f.readlines()
        result_lines = run_data(all_lines)
        for line in result_lines:
            print(" ".join(map(str, line)))
