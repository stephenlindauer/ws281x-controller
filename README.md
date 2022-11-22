# ws281x-controller



A service and tool to manage the ws281x light strips for my home. 

This library is a wrapper around [rpi-ws281x-python](https://github.com/rpi-ws281x/rpi-ws281x-python) to provide more advanced and customizable setups. The `LEDSystem` is made up of components you define in a `componentConfig`. Components can be any sections of the light strip however you decide to break it up. Each component has 'programs' attached to it to define how you want it to look. The programs I wrote focus on changing/animating lights, but static/non-animating lights are possible too.

The project also includes a webserver that contains a visualizer/simulator and a simple API for controlling the lights.

The motivation behind the visualizer/simulator is to allow building / testing different animations without needing to run it on a Raspberry Pi or while having access to light strips. This makes for a much quicker development cycle and allowing you to test changes without interrupting the lights on your home.

![](https://stephenlindauer.s3.us-west-1.amazonaws.com/lights.gif)


## Setup

```bash
# Setup a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running
```bash
sudo python3 controller.py
```

