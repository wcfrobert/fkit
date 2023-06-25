<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/logo.png?raw=true" alt="logo" style="zoom:50%;" />
  <br>
  Fiber Section Analysis in Python
  <br>
</h1>

<p align="center">
Define fiber stress-strain properties. Mesh section. Perform moment-curvature and PM interaction surface analysis with ease.
</p>

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 100%;" />
</div>





TODO: ADD TOC HERE




## Introduction

TODO







## Quick Start

**Installation**

See "Installation" section below for more info. For casual users, use Anaconda Python, download this module, and open "main.py" in Spyder IDE.

**Using fkit**

```python
# import fkit
import fkit
from fkit.plotter import plot_MK, plot_PM_ACI
from fkit.patchfiber import Hognestad
from fkit.nodefiber import Bilinear

# define fibers
fiber_concrete = Hognestad(fpc=5)
fiber_steel    = Bilinear(fy=60)

# Most common sections can be defined with SectionBuilder
section1 = fkit.sectionbuilder.rectangular(width = 24, height = 24, cover = 1.5,
                                           top_bar = [0.6, 2, 1, 0],
                                           bot_bar = [0.6, 4, 2, 3],
                                           concrete_fiber = fiber_concrete,
                                           steel_fiber = fiber_steel)

# moment curvature
section1.run_moment_curvature()

# P+M interaction
section1.run_interaction_ACI(fpc=5, fy=60)

# plot results
plot_MK(section1)
plot_PM_ACI(section1)

# export results to csv
section1.export_data()
```



## Installation

**<u>Option 1: Anaconda Python Distribution</u>**

For the casual users, using the base Anaconda Python environment is recommended. This is by far the easiest method of installation. Users don't need to worry about dependencies and setting up virtual environments. The following packages are used in this project:

* Numpy
* Matplotlib
* Scipy
* Pandas

Installation procedure:

1. Download Anaconda python
2. Download this package (click the green "Code" button and download zip file)
3. Open and run "main.py" in Anaconda's Spyder IDE. Make sure working directory is correctly configured.


**<u>Option 2: Vanilla Python</u>**

1. Download this project to a folder of your choosing
    ```
    git clone https://github.com/wcfrobert/fkit.git
    ```
2. Change directory into where you downloaded fkit
    ```
    cd fkit
    ```
3. Create virtual environment
    ```
    py -m venv venv
    ```
4. Activate virtual environment
    ```
    venv\Scripts\activate
    ```
5. Install requirements
    ```
    pip install -r requirements.txt
    ```
6. run fkit
    ```
    py main.py
    ```

Note that pip install is available.

```
pip install fkit
```




## Usage


TODO


## Fiber Stress-Strain Models

TODO

## SectionBuilder Templates

TODO

## Theoretical Background: Moment Curvature

TODO


## Theoretical Background: P+M Interaction Surface

TODO

## Notes and Assumptions

TODO


## License

MIT License

Copyright (c) 2023 Robert Wang
