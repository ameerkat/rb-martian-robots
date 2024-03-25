from main import World

def test_run_sample_data():
    world = World(5, 3)
    assert world.run_robot(1, 1, "E", "RFRFRFRF") == (1, 1, "E")
    assert world.run_robot(3, 2, "N", "FRRFLLFFRRFLL") == (3, 3, "N", "LOST")
    world.run_robot(0, 3, "W", "LLFFFLFLFL") == (2, 3, "S")
