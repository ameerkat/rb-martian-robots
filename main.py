"""
Martian Robots
Usage example:
python main.py input.txt

The input file should contain the world dimensions and robot data as per the problem statement.
"""

import argparse
import json
import base64
import urllib.parse

class Robot:
    """
    Represents a robot on Mars. The robot has a position and a direction it is facing.
    Logic for the direction and changing direction is encapsulated in the class, however
    navigation logic is handled by the Mars class as the robot's actions are dictated by
    the world it is in.
    """

    def __init__(self, x, y, direction):
        if direction not in ["N", "E", "S", "W"]:
            raise ValueError(f"Invalid direction: {direction}")
        self.x = x
        self.y = y
        self.direction = direction

    def rotate_left(self):
        """Rotates a robot 90 degrees to the left."""
        if self.direction == "N":
            self.direction = "W"
        elif self.direction == "E":
            self.direction = "N"
        elif self.direction == "S":
            self.direction = "E"
        elif self.direction == "W":
            self.direction = "S"
        else:
            raise ValueError(f"Invalid direction: {self.direction}")
        
    def rotate_right(self):
        """Rotates a robot 90 degrees to the right."""
        if self.direction == "N":
            self.direction = "E"
        elif self.direction == "E":
            self.direction = "S"
        elif self.direction == "S":
            self.direction = "W"
        elif self.direction == "W":
            self.direction = "N"
        else:
            raise ValueError(f"Invalid direction: {self.direction}")

    def __str__(self):
        return f"{self.x} {self.y} {self.direction}"


class Mars:
    """
    Represents the world on Mars. The world is a grid of width x height.
    """

    @staticmethod
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

    def __init__(self, top_x, top_y):
        if (top_x < 0 or top_x > 50
            or top_y < 0 or top_y > 50):
            raise ValueError(f"Invalid coordinates: {top_x}, {top_y}. Min 0, Max 50.")
        self.width = top_x + 1
        self.height = top_y + 1
        self.word_state = Mars._get_initial_world(self.width, self.height)

    def run_robot(self, x, y, direction, instructions):
        """
        Runs a robot from a starting position and direction with a set of instructions.
        """

        if (x < 0 or x >= self.width) or (y < 0 or y >= self.height):
            raise ValueError(f"Invalid robot starting position: {x}, {y}")

        # This is the actual logic to run the robots. This does mutate the world.
        # Because the actions of the robot are dictated by the world, and robots
        # can mutate the world through falling off, we will simply use the robot 
        # as a container for the robot state rather than any logic.
        robot = Robot(x, y, direction)
        for instruction in instructions:
            out_of_bounds_check_required = False

            if instruction == "F":
                if robot.direction == "N":
                    if robot.y == self.height - 1: # Out of Bounds: Robot at Top of World
                        out_of_bounds_check_required = True
                    else:
                        robot.y += 1
                elif robot.direction == "E":
                    if robot.x == self.width - 1: # Out of Bounds: Robot at Right of World
                        out_of_bounds_check_required = True
                    else:
                        robot.x += 1
                elif robot.direction == "S":
                    if robot.y == 0: # Out of Bounds: Robot at Bottom of World
                        out_of_bounds_check_required = True
                    else:
                        robot.y -= 1
                elif robot.direction == "W":
                    if robot.x == 0: # Out of Bounds: Robot at Left of World
                        out_of_bounds_check_required = True
                    else:
                        robot.x -= 1
                else:
                    raise ValueError(f"Invalid direction: {robot.direction}")
            elif instruction == "L":
                robot.rotate_left()
            elif instruction == "R":
                robot.rotate_right()
            else:
                raise ValueError(f"Invalid instruction: {instruction}")

            if out_of_bounds_check_required:
                # World state false means the robot can go out of bounds. True means
                # a previous robot was lost here and we ignore the instruction.
                if not self.word_state[robot.y][robot.x]:
                    self.word_state[robot.y][robot.x] = True
                    return robot.x, robot.y, robot.direction, "LOST"

        return robot.x, robot.y, robot.direction


def run_data(lines):
    """
    Takes a list of lines and runs the simulation, returning a list of result states.
    """

    result = []

    max_coordinate_data = lines[0].split()
    if len(max_coordinate_data) != 2:
        raise ValueError("Invalid world spec. Must have 2 components width and height.")
    top_x, top_y = map(int, max_coordinate_data)
    world = Mars(top_x, top_y)

    line_i = 1 # skip the first line which is the world data
    while line_i < len(lines):
        # skip over the line that breaks up the robot data
        if lines[line_i].strip() == "":
            line_i += 1
            continue
        x, y, direction = lines[line_i].split()
        if line_i + 1 >= len(lines):
            raise ValueError("Invalid robot data. Missing instructions.")
        instructions = lines[line_i + 1].strip()
        x, y = map(int, [x, y])
        result.append(world.run_robot(x, y, direction, instructions))
        line_i += 2

    return result


def lambda_handler(event, context):
    """
    Entry point for the AWS Lambda function. This function will handle both GET and POST requests.
    for a quick and dirty web interface to the Martian Robots problem. UI is not a focus for
    this implementation, so the form is very basic.
    """
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
        # remove "data=" from the form encoded body, for more complex
        # implementations we should parse out the form data properly.
        data = urllib.parse.unquote_plus(event["body"][5:])
        print(data)
        lines = data.split("\n")
        try:
            output_lines = run_data(lines)
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/plain"
                },
                "body": "\n".join(" ".join(map(str, line)) for line in output_lines)
            }
        except ValueError as e:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "text/plain"
                },
                "body": str(e)
            }


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Martian Robots")
    parser.add_argument("file",
                        help="The input file name containing the formatted world and robot data. As per the problem statement specifications.",
                        type=str)
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        result_lines = run_data(all_lines)
        for line in result_lines:
            print(" ".join(map(str, line)))
