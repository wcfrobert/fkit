<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/logo.png?raw=true" alt="logo" style="zoom:50%;" />
  <br>
  Fiber Section Analysis in Python
  <br>
</h1>
<p align="center">
Define fiber stress-strain model. Create section. Perform moment-curvature and PM interaction analysis with ease.
</p>


<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 100%;" />
</div>




- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Fiber Stress-Strain Models](#fiber-stress-strain-models)
- [SectionBuilder Templates](#sectionbuilder-templates)
- [Theoretical Background: Moment Curvature](#theoretical-background--moment-curvature)
- [Theoretical Background: P+M Interaction Surface](#theoretical-background--p-m-interaction-surface)
- [Notes and Assumptions](#notes-and-assumptions)
- [License](#license)



## Introduction

fkit (fiber-kit) is a fiber section analysis program built with python. It is incredibly powerful, flexible, and easy to use. Perform moment-curvature and P+M interaction analysis with ease! Originally meant for reinforced concrete sections, I realized during development that the concept of strain compatibility (i.e incrementally increasing curvature and then searching for a neutral axis depth that satisfies equilibrium) applies to any material; as long as "plane-section-remain-plane".


<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/hello_demo.png?raw=true" alt="demo" style="width: 100%;" />
</div>


Notable Features:

* Large selection of built-in material models (Hognestad, Mander, Todeschini, Ramberg-Osgood, Menegotto-Pinto, and more)
* Moment curvature analysis
* P+M interaction analysis
* Fast and Intuitive to use. Run moment curvature with 4 lines of code
* Sections can be easily defined with SectionBuilder
* Beautiful visualizations
* Flexible and transparent. Export data and view fiber stress-strain

I made this because OpenseesPy is overkill for moment curvature analysis. Why define zero-length elements, integrators, DOF numbering, displacement control, what...? Anyways, I digress. I thought the end-product was aesthetically pleasing both in the visualizations and the back-end object-oriented design. Enjoy!


**Disclaimer:** this package is meant for <u>personal or educational use only</u>. Fiber kit is a one-person passion project, not an enterprise-grade software. I did not spent much time debugging all the edge cases. fkit should not be used for commercial purpose of any kind!


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

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo2.png?raw=true" alt="demo" style="width: 100%;" />
</div>



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

```python
import fkit

"""
#########################################
Step 1: Define fibers
#########################################
"""
# define fiber material properties
fiber_unconfined = fkit.patchfiber.Todeschini(fpc=5, eo=0.002, emax=0.006, default_color="lightgray")
fiber_confined   = fkit.patchfiber.Mander(fpc=6, eo=0.004, emax=0.014, default_color="gray")
fiber_steel      = fkit.nodefiber.Bilinear(fy=60, beta=0.01, emax=0.16, default_color="black")

# plot and adjust fiber as needed
fkit.plotter.preview_fiber(fiber_unconfined, x_limit=[-0.008, 0.008])
fkit.plotter.preview_fiber(fiber_confined, x_limit=[-0.03, 0.03])
fkit.plotter.preview_fiber(fiber_steel, x_limit=[-0.03, 0.03])


"""
#########################################
Step 2: Define section
#########################################
"""
# for the most flexibility, user may define section manually patch by patch
section1 = fkit.section.Section()
section1.add_patch(xo=1.5, yo=1.5, b=12 ,h=21, nx=1, ny=10, fiber=fiber_confined)
section1.add_patch(xo=1.5, yo=0, b=12 ,h=1.5, nx=1, ny=2, fiber=fiber_unconfined)
section1.add_patch(xo=1.5, yo=22.5, b=12 ,h=1.5, nx=1, ny=2, fiber=fiber_unconfined)
section1.add_patch(xo=0, yo=0, b=1.5 ,h=24, nx=1, ny=10, fiber=fiber_unconfined)
section1.add_patch(xo=13.5, yo=0, b=1.5 ,h=24, nx=1, ny=10, fiber=fiber_unconfined)
section1.add_bar_group(xo=1.5, yo=1.5, b=12, h=21, nx=3, ny=3, area=0.6, perimeter_only=True, fiber=fiber_steel)

# finalize geometry. The user has the ability to rotate the section
section1.mesh(rotate=45)

# alternatively, most common sections can be quickly defined with SectionBuilder
section2 = fkit.sectionbuilder.rectangular_confined(width = 15, 
                                                    height = 24, 
                                                    cover = 1.5, 
                                                    top_bar = [0.6, 3, 1, 0], 
                                                    bot_bar = [0.6, 3, 1, 0], 
                                                    core_fiber = fiber_confined, 
                                                    cover_fiber = fiber_unconfined, 
                                                    steel_fiber = fiber_steel)

# the user can make additional customizations, but make sure to mesh afterwards.
section2.add_bar(coord=[-6,0], area=0.6, fiber=fiber_steel)
section2.add_bar(coord=[6,0], area=0.6, fiber=fiber_steel)
section2.mesh()

# preview section
fkit.plotter.preview_section(section1)
fkit.plotter.preview_section(section2)


"""
#########################################
Step 3: Moment curvature analysis
#########################################
"""
# moment-curvature analysis
section2.run_moment_curvature(P=-180, phi_max=0.002, N_step=100)

# plot results
fkit.plotter.plot_MK(section2)

# put strain gauge at a fiber and retrieve data
bot_rebar_data = section2.get_node_fiber_data(tag=3)
fiber_data = section2.get_patch_fiber_data(location=[0,8])
top_fiber_data = section2.get_patch_fiber_data(location="top")
bot_fiber_data = section2.get_patch_fiber_data(location="bottom")

# # animate results
# fkit.plotter.animate_MK(section2)


"""
#########################################
Step 4: PMM interaction analysis
#########################################
"""
# generate PM interaction surface using user-defined fibers
section2.run_interaction(ecu=0.004)

# generate PM interaction surface using ACI-318 assumptions (rectangular stress block + EPP rebar)
section2.run_interaction_ACI(fpc=6, fy=60)

# plot PM interaction surface
fkit.plotter.plot_PM_ACI(section2, P=[-50,400], M=[-500,3000])
fkit.plotter.plot_PM(section2, P=[50,400], M=[-500,3000])


"""
#########################################
Step 5: Data export
#########################################
"""
# export all data to csv
section2.export_data()
```




## Fiber Stress-Strain Models

TODO

Concrete:
* Hognestad et al (1951)
* Mander et al (1988)
* Todeschini et al (1964)

Steel:
* Bilinear
* Multilinear - Rex & Easterling (1996)
* RambergOsgood
* MenegottoPinto
* Custom_Trilinear



## SectionBuilder Templates

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/sectionbuilder.png?raw=true" alt="demo" style="width: 100%;" />
</div>


## Theoretical Background: Moment Curvature

TODO


## Theoretical Background: P+M Interaction Surface

TODO




## Notes and Assumptions

* +P is tension, -P is compression 
* fkit is agnostic when it comes to unit. Please ensure your input is consistent. I tend to use kips and inches



## License

MIT License

Copyright (c) 2023 Robert Wang
