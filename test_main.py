from main import World

def test_coordinates():
    world = World(5, 5)
    assert world.width == 5
    assert world.height == 5

    # the coordinates of 0, 0 (the bottom left) are internally represented
    # as 0, 4 the bottom left.
    assert world._translate_coordinate_to_index(0, 0) == (0, 4)

    # the coordinates of 4, 4 (the top right) are internally represented
    # as 4, 0 the bottom right.
    assert world._translate_coordinate_to_index(4, 4) == (4, 0)

    # the indices of 0, 4 (the bottom left) are represented
    # as 0, 0 in the coordinate system.
    assert world._translate_index_to_coordinate(0, 4) == (0, 0)

    # the indices of 4, 0 (the bottom right) are represented
    # as 4, 4 in the coordinate system.
    assert world._translate_index_to_coordinate(4, 0) == (4, 4)
