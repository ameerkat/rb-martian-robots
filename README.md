# Usage
## Running Tests
You need `pytest` on your system to run the tests. There are no non-standard
library dependencies, so you can simply `pip3 install pytest` or equivalent
on your system, or set up a virtual environment and install the `requirements.txt`
via `pip3 install -r requirements.txt`.

To run tests run `pytest`.

## Running Sample Data Files
You can run the sample data by calling the script e.g. `python3 main.py sample_data.txt`, passing
the file you want to process as the first positional parameter.

## Running Sample Data Online
You can also run sample data from the web with a simple lambda interface at
[https://f55xysqwn6dfq3ry55d4jk52lu0mzrgr.lambda-url.us-east-1.on.aws/](https://f55xysqwn6dfq3ry55d4jk52lu0mzrgr.lambda-url.us-east-1.on.aws/). The interface
is all contained in lambda_handler and has a text area you can paste your data
to process.

### Deployment
You can run this lamdba yourself by copying the entire main as the lambda 
function code with lambda_handler (the default name anyway) as the entry point. 
There are no external dependencies so packaging is not necessary.

# Solution Discussion
The approach taken was to let the world contain the logic to run the simulation,
represented by the class World. The robots (class Robot) act as a 
container for coordinates and direction. The world owns the
interface to run the simulation, and tracks where robots fall off the grid. The
World class is then wrapped to expose it to different interfaces such as a CLI
and a small lambda based web interface.

# Design Decisions
## Coding Language
After reviewing the project statement **Python** was chosen as the language of 
choice due to the following properties

* Personal familiarity. Because of the tight timeframe of the project we want
to ensure strong familiarity with a language and its standard library. This
means Java, Python, C#, and JS/TS were considered.
* In the specifications it can be deduced that the path of one robot can have
an effect on subsequent robot if it is "lost" (goes out of bounds). This 
tells me that parllelism (something other languages might be stronger with
due to the lack of the global interpreter lock) is not a priority.
* The project can be modeled in a small number of classes, with most of the
code base being in the application logic rather than the class structure.
* There is file IO, and the opportunity for a small CLI. Both of these are
easily achievable in Python whereas the overhead for such things in some other 
languages considered (Java, C#, JS) are more complex.
* We can provide a simple web interface by deploying this as a lambda URL. This
is not a priority but a nice quality of life feature that is easily achievable 
with Python. In an actual client scenario this enables non-technical users
easy access without a lot of effort or maintainence.