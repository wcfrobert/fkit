<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/logo.png?raw=true" alt="logo" style="zoom:50%;" />
  <br>
  Fiber Section Analysis in Python
  <br>
</h1>
<p align="center">
Define fiber material properties, create section, perform moment-curvature and PM interaction analysis with ease.
</p>





<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 100%;" />
</div>


- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Notes and Assumptions](#notes-and-assumptions)
- [License](#license)




## Introduction

fkit (fiber-kit) is a section analysis program implemented in Python. It is incredibly powerful, flexible, and easy-to-use. Perform **moment-curvature** and **P+M interaction** analysis with very few lines of code. Originally meant for reinforced concrete sections, it was later extended to all material type (e.g. wood, steel, FRPs, anything that can be defined by a stress-strain curve). 

Notable Features:

* Large selection of material models (Hognestad, Mander, Todeschini, Ramberg-Osgood, Menegotto-Pinto, Bilinear, Trilinear, Multilinear)
* Moment curvature analysis
* P+M interaction analysis
* Fast and Intuitive to use. Run moment curvature with 4 lines of code
* Rotate section to any orientation
* Sections can be quickly defined with SectionBuilder
* Beautiful visualizations
* Flexible and transparent. Export data and view fiber stress/strain progression


<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/hello_demo.png?raw=true" alt="demo" style="width: 100%;" />
</div>


**Disclaimer:** this package is meant for <u>personal or educational use only</u>. Fiber kit is a one-person passion project, not an enterprise-grade software.I did not allot much time for debugging or testing. fkit should not be used for commercial purpose of any kind!






## Quick Start

**Installation**

See "Installation" section below for more info. For casual users, use Anaconda Python, download this module, and run within Spyder IDE.

**Quick Start Script**

Run main_quickstart.py:

```python
# import fkit
import fkit

# define fibers
fiber_concrete = fkit.patchfiber.Hognestad(fpc=4, take_tension=True)
fiber_steel    = fkit.nodefiber.Bilinear(fy=60, Es=29000)

# create a rectangular beam section with SectionBuilder
section1 = fkit.sectionbuilder.rectangular(width = 18, 
                                           height = 24, 
                                           cover = 2, 
                                           top_bar = [0.6, 4, 1, 0], 
                                           bot_bar = [0.6, 4, 2, 3],  
                                           concrete_fiber = fiber_concrete, 
                                           steel_fiber = fiber_steel)

# moment curvature and PM interaction
MK_results = section1.run_moment_curvature(phi_target=0.0004)
PM_results = section1.run_PM_interaction(fpc=4, fy=60, Es=29000)

# plot results
fkit.plotter.plot_MK(section1)
fkit.plotter.plot_PM(section1)
```

Three other sample scripts are provided to help get the users up and running:

* `main_full.py` - illustrates all the major functionalities of fkit
* `main_notebook.ipynb` - for users more accustomed to notebook environments
* `main_fiber.py` - illustrates many of the material models within fkit

The above example script uses US imperial unit **(kips, in, ksi)**. You may also use SI units **(N, mm, MPa)**. 

`plot_MK()` and `plot_PM()` produces the visualizations below. `export_data()` generates a result folder in the current working directory.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo2.png?raw=true" alt="demo" style="width: 80%;" />
</div>

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo3.png?raw=true" alt="demo" style="width: 80%;" />
</div>




## Installation

**Option 1: Anaconda Python Distribution**

For the casual users, using the base Anaconda Python environment is recommended. This is by far the easiest method of installation. Users don't need to worry about dependencies and setting up virtual environments. The following packages are used in this project:

* Numpy
* Matplotlib
* Scipy
* Pandas

Installation procedure:

1. Download Anaconda python
2. Download this package (click the green "Code" button and download zip file)
3. Open and run "main.py" in Anaconda's Spyder IDE. Make sure working directory is correctly configured.

**Option 2: Vanilla Python**

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

Here is a sample script that illustrates most of the functionalities of fkit.

```python
import fkit

"""
#########################################
Step 1: Define fiber material properties
#########################################
"""
# define fiber material properties
fiber_unconfined = fkit.patchfiber.Todeschini(fpc=5)
fiber_confined   = fkit.patchfiber.Mander(fpc=6, eo=0.004, emax=0.014, default_color="gray")
fiber_steel      = fkit.nodefiber.Bilinear(fy=60, fu=90, Es=29000)

# preview fibers
fkit.plotter.preview_fiber(fiber_unconfined, x_limit=[-0.008, 0.008])
fkit.plotter.preview_fiber(fiber_confined, x_limit=[-0.03, 0.03])
fkit.plotter.preview_fiber(fiber_steel, x_limit=[-0.03, 0.03])



"""
#########################################
Step 2: Define sections
#########################################
"""
# user may create sections manually
section1 = fkit.section.Section()

section1.add_patch(xo=0, yo=0, b=18 ,h=18, nx=25, ny=25, fiber=fiber_unconfined)

section1.add_bar_group(xo=2, yo=2, b=14, h=14, nx=3, ny=3, area=0.6, perimeter_only=True, fiber=fiber_steel)

section1.mesh(rotate=45)


# most common sections can be quickly defined with SectionBuilder
section2 = fkit.sectionbuilder.rectangular_confined(width = 15, 
                                                    height = 24, 
                                                    cover = 1.5, 
                                                    top_bar = [0.6, 3, 1, 0], 
                                                    bot_bar = [0.6, 3, 1, 0], 
                                                    core_fiber = fiber_confined, 
                                                    cover_fiber = fiber_unconfined, 
                                                    steel_fiber = fiber_steel,
                                                    mesh_nx=0.75,
                                                    mesh_ny=0.75)

# preview section
fkit.plotter.preview_section(section1)
fkit.plotter.preview_section(section2, show_tag=True)



"""
#########################################
Step 3: Moment curvature analysis
#########################################
"""
# moment-curvature analysis
phi_yield_approximate = 0.003 / (0.25*18)
MK_results = section2.run_moment_curvature(phi_target = phi_yield_approximate, P=-180)

# obtain stress/strain history of any fiber
fiber_data        = section2.get_patch_fiber_data(location=[0.0, 8.25])
fiber_data_top    = section2.get_patch_fiber_data(location="top")
fiber_data_bottom = section2.get_patch_fiber_data(location="bottom")
fiber_data_rebar3 = section2.get_node_fiber_data(tag=3)

# plot results
fkit.plotter.plot_MK(section2)

# animate results
# fkit.plotter.animate_MK(section2)


"""
#########################################
Step 4: PMM interaction analysis
#########################################
"""
# generate PM interaction surface using ACI-318 assumptions
PM_results = section2.run_PM_interaction(fpc=6, fy=60, Es=29000)

# plot PM interaction surface
fkit.plotter.plot_PM(section2, P=[50,400], M=[-500,3000])


"""
#########################################
Step 5: Data export
#########################################
"""
# export all data to csv
section2.export_data()

```



Here is a comprehensive list of all the commands that is available to the user. 

**Defining material properties**

* `fkit.patchfiber.Hognestad()`
* `fkit.patchfiber.Todeschini()`
* `fkit.patchfiber.Mander()`
* `fkit.patchfiber.Bilinear()`
* `fkit.patchfiber.Multilinear()`
* `fkit.patchfiber.RambergOsgood()`
* `fkit.patchfiber.MenegottoPinto()`
* `fkit.patchfiber.Custom_Trilinear()`
* `fkit.nodefiber.Bilinear()`
* `fkit.nodefiber.Multilinear()`
* `fkit.nodefiber.RambergOsgood()`
* `fkit.nodefiber.MenegottoPinto()`
* `fkit.nodefiber.Custom_Trilinear()`



**Defining sections manually**

* `fkit.section.add_patch()`
* `fkit.section.add_bar_group()`
* `fkit.section.add_bar()`
* `fkit.section.mesh()`



**Defining sections with SectionBuilder**

* `fkit.sectionbuilder.rectangular()`
* `fkit.sectionbuilder.rectangular_confined()`
* `fkit.sectionbuilder.circular()`
* `fkit.sectionbuilder.flanged()`
* `fkit.sectionbuilder.wall()`
* `fkit.sectionbuilder.wall_BE()`
* `fkit.sectionbuilder.wall_layered()`
* `fkit.sectionbuilder.wall_speedcore()`
* `fkit.sectionbuilder.wide_flange()`
* `fkit.sectionbuilder.W_AISC()`
* `fkit.sectionbuilder.W_AISC_composite()`



**Section analysis commands**

* `fkit.section.run_moment_curvature()`
* `fkit.section.run_PM_interaction()`
* `fkit.section.get_node_fiber_data()`
* `fkit.section.get_patch_fiber_data()`
* `fkit.section.export_data()`



**Visualization**

* `fkit.plotter.preview_fiber()`
* `fkit.plotter.preview_section()`
* `fkit.plotter.plot_MK()`
* `fkit.plotter.animate_MK()`
* `fkit.plotter.plot_PM()`



In addition to the documentation provided in the `\doc` folder, the user may easily access docstrings of any methods:

```python
help(fkit.patchfiber.Hognestad)
fkit.patchfiber.Hognestad?
```

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/helpcommand.png?raw=true" alt="demo" style="width: 90%;" />
</div>





## Notes and Assumptions

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/signconvention.png?raw=true" alt="demo" style="width: 45%;" />
</div>



* Sign conventions: 
  * +ve is tensile stress/strain, 
  * -ve is compressive stress/strain
* Please ensure consistent unit input:
  * SI Unit: **(N, mm, MPa)**
  * Freedom Unit: **(kips, in, ksi)**
* Node fibers and patch fibers often overlap within the compression region. Consequently, some forces will be double counted. For most lightly reinforced sections, the change to the final result is insignificant and we simplify the problem without any appreciable loss in accuracy by just ignoring this overlap.
* Currently, the PM interaction analysis routine follows ACI 318-19 assumptions (e.g. rectangular stress block, elastic-perfect-plastic steel, spalling strain of 0.003, etc)



**Refer to the README in `\doc` folder for detailed documentation along with theoretical background.** 


## License

MIT License

Copyright (c) 2023 Robert Wang
