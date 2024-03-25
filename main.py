class World:
    def _get_initial_world(width, height):
        # We'll represent the world as a 2D array of booleans. True means that
        # a robot was lost at that cell. False means the cell is in it's default
        # state and a robot can go out of bounds from it. In theory we can 
        # represent the world with just the perimeter as per the problem statement. 
        # But for simplicity we'll represent the whole world.
        return [[False for x in range(width)] for y in range(height)]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.world = World._get_initial_world(width, height)

    def _translate_coordinate_to_index(self, x, y):
        # The world is represented where the origin is at the bottom left
        # and the top right is (width, height). This is in contrast to our array
        # indices where 0,0 is top left and width, height is bottom right. We 
        # need to translate the coordinates to the 2D array index at initialization.

        # By separating out the translation logic, we can put a robot where it should
        # be and keep the directionality the same. N can remain "up" a row.
        return (x, self.height - y - 1)
    
    def _translate_index_to_coordinate(self, i, j):
        # When we need to return the coordinates to the user, we need to translate
        # the 2D array index back to the coordinate system.
        return (i, self.height - j - 1)

    def reset(self):
        self.world = World._get_initial_world(self.width, self.height)

    def run(self, robot):
        pass