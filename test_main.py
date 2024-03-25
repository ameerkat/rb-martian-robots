from main import World
from main import lambda_handler, run_data

# TODO we could make more assertions about the kind of errors that are raised.

def test_run_sample_data():
    world = World(5, 3) # 6x4 grid for top coordinates 5,3
    assert world.run_robot(1, 1, "E", "RFRFRFRF") == (1, 1, "E")
    assert world.run_robot(3, 2, "N", "FRRFLLFFRRFLL") == (3, 3, "N", "LOST")
    assert world.run_robot(0, 3, "W", "LLFFFLFLFL") == (2, 3, "S")

def test_world_too_big():
    try:
        world = World(51, 51)
        assert False
    except ValueError as e:
        assert e

def test_world_too_small():
    try:
        # Note that a 0, 0 world is valid, it's size 1x1
        world = World(-1, -1)
        assert False
    except ValueError as e:
        assert e

def test_invalid_robot_starting_position():
    world = World(5, 3)
    try:
        world.run_robot(6, 4, "E", "RFRFRFRF")
        assert False
    except ValueError as e:
        assert e

def test_invalid_direction():
    world = World(5, 3)
    try:
        world.run_robot(0, 0, "T", "RFRFRFRF")
        assert False
    except ValueError as e:
        assert e

def test_invalid_instruction():
    world = World(5, 3)
    try:
        world.run_robot(0, 0, "E", "RRLLRB")
        assert False
    except ValueError as e:
        assert e

def test_run_data():
    result = run_data("""5 3
1 1 E
RFRFRFRF
                      
3 2 N
FRRFLLFFRRFLL
                      
0 3 W
LLFFFLFLFL""".split("\n"))
    assert result == [(1, 1, "E"), (3, 3, "N", "LOST"), (2, 3, "S")]

def test_run_data_with_empty_instructions():
    result = run_data("""5 3
1 1 E
RFRFRFRF
                      
3 2 N

              
0 3 W
LF""".split("\n"))
    print(result)
    assert result == [(1, 1, "E"), (3, 2, "N"), (0, 2, "S")]

def test_missing_run_data():
    try:
        result = run_data("""5 3
    1 1 E
    RFRFRFRF
                        
    3 2 N
    FRRFLLFFRRFLL
                        
    0 3 W""".split("\n"))
        assert False
    except ValueError as e:
        assert e

def test_malformed_initial_robot_state_run_data():
    try:
        result = run_data("""5 3
    1 1 E
    RFRFRFRF
                        
    3 2 N
    FRRFLLFFRRFLL
                        
    0 3
    LLFFFLFLFL""".split("\n"))
        assert False
    except ValueError as e:
        assert e

def test_lambda_entry_post():
    response = lambda_handler({
        "requestContext": {
            "http": {
                "method": "POST",
                "path": "/",
                "protocol": "HTTP/1.1"
            }
        },
        # TODO make this derived from sample data and encode it here in test
        "body": "ZGF0YT01KzMlMEQlMEExKzErRSslMEQlMEFSRlJGUkZSRislMEQlMEElMEQlMEEzKzIrTiUwRCUwQUZSUkZMTEZGUlJGTEwrJTBEJTBBKyUwRCUwQTArMytXJTBEJTBBTExGRkZMRkxGTA==",
        "isBase64Encoded": True
    }, None)
    assert response["statusCode"] == 200
    assert response["body"] == """1 1 E
3 3 N LOST
2 3 S"""