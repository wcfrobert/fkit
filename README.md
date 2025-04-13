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

fkit (fiber-kit) is a section analysis program implemented in Python. It is powerful, flexible, and easy-to-use. Perform **moment-curvature** and **P+M interaction** analysis with very few lines of code. Originally meant for reinforced concrete sections, it was later extended to all material type (e.g. wood, steel, FRPs, anything that can be defined by a stress-strain curve). 

Notable Features:

* Large selection of material models (Hognestad, Mander, Todeschini, Ramberg-Osgood, Menegotto-Pinto, Bilinear, Trilinear, Multilinear)
* Moment curvature analysis
* P+M interaction analysis
* Cracked moment of inertia calculations
* Fast, Intuitive to use, and fully transparent. View stress/strain data of every fiber at each load step
* Great looking visualizations


<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/hello_demo.png?raw=true" alt="demo" style="width: 100%;" />
</div>




## Quick Start

Run main_quickstart.py:

```python
# import fkit
import fkit

# define concrete and steel fibers
fiber_concrete = fkit.patchfiber.Hognestad(fpc=4, take_tension=True)
fiber_steel    = fkit.nodefiber.Bilinear(fy=60, Es=29000)

# create a rectangular beam section with SectionBuilder
section1 = fkit.sectionbuilder.rectangular(width = 18, 
                                           height = 24, 
                                           cover = 2, 
                                           top_bar = [0.6, 4, 1, 0], #[bar_area, nx, ny, y_spacing]
                                           bot_bar = [0.6, 4, 2, 3], #[bar_area, nx, ny, y_spacing] 
                                           concrete_fiber = fiber_concrete, 
                                           steel_fiber = fiber_steel)

# moment curvature
MK_results = section1.run_moment_curvature(phi_target=0.0003)
df_nodefibers, df_patchfibers = section1.get_all_fiber_data()

# cracked moment of inertia
Icr_results = section1.calculate_Icr(Es=29000, Ec=3605)

# PM Interaction surface analysis
PM_results = section1.run_PM_interaction(fpc=4, fy=60, Es=29000)

# plot results
fkit.plotter.plot_MK(section1)
fkit.plotter.plot_PM(section1)
fkit.plotter.plot_Icr(section1)
```

Three other sample scripts are provided to help get the users up and running:

* `main_full.py` - illustrates all the major functionalities of fkit
* `main_fiber.py` - illustrates many of the material models within fkit
* `main_sectionbuilder.py` - illustrates some of the common sections that can be created with sectionBuilder
* `main_notebook.ipynb` - for users more accustomed to notebook environments

The above example script uses US imperial unit **(kips, in, ksi)**. You may also use SI units **(N, mm, MPa)**. The quick start script produces the following visualizations:

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo2.png?raw=true" alt="demo" style="width: 80%;" />
</div>

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo3.png?raw=true" alt="demo" style="width: 80%;" />
</div>
<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/Icr.png?raw=true" alt="demo" style="width: 80%;" />
</div>



## Installation

**Option 1: Anaconda Python**

This is the simplest way to get started.

1. Download Anaconda python distribution: [https://www.anaconda.com/download](https://www.anaconda.com/download)
2. Download this package (click the green "Code" button and download zip file or download the latest release)
3. Open and run "main.py" in Anaconda's Spyder IDE

**Option 2: Regular Python**

1. Download python: [https://www.python.org/](https://www.python.org/)
2. Download this project to a folder of your choosing
    ```
    git clone https://github.com/wcfrobert/fkit.git
    ```
3. Change directory into where you downloaded fkit
    ```
    cd fkit
    ```
4. Create virtual environment
    ```
    py -m venv venv
    ```
4. Activate virtual environment
    ```
    venv\Scripts\activate
    ```
6. Install requirements
    ```
    pip install -r requirements.txt
    ```
7. run fkit
    ```
    py main.py
    ```

Note that pip install is available.

```
pip install fiberkit
```

Fiberkit was developed using python 3.12 (any version above 3.7 will probably work as well) with the following dependencies.

* Numpy
* Matplotlib
* Pandas



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
# Option 1: draw section manually
section1 = fkit.Section()
section1.add_patch(xo=0, yo=0, b=18 ,h=18, nx=25, ny=25, fiber=fiber_unconfined)
section1.add_bar_group(xo=2, yo=2, b=14, h=14, nx=3, ny=3, area=0.6, perimeter_only=True, fiber=fiber_steel)
section1.mesh()

# Option 2: most sections can be defined with SectionBuilder
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
# roughly estimate target curvature, which is a measure of how much to push the section.
phi_yield = 0.003 / (0.25*24)

# moment-curvature analysis
MK_results = section2.run_moment_curvature(phi_target = phi_yield, P=-180)

# calculate cracked moment of inertia at each load step
Icr_results = section2.calculate_Icr(Es=29000, Ec=3605)

# extract all fiber data
df_nodefibers, df_patchfibers = section2.get_all_fiber_data()

# extract data of a specific fiber
fiber_data        = section2.get_patch_fiber_data(location=[0.0, 8.25])
fiber_data_top    = section2.get_patch_fiber_data(location="top")
fiber_data_bottom = section2.get_patch_fiber_data(location="bottom")
fiber_data_rebar3 = section2.get_node_fiber_data(tag=3)

# plot results
fkit.plotter.plot_MK(section2)
fkit.plotter.plot_Icr(section2)

# animate results
# fkit.plotter.animate_MK(section2)


"""
#########################################
Step 4: PMM interaction analysis
#########################################
"""
# generate PM interaction surface using ACI-318 provisions
PM_results = section2.run_PM_interaction(fpc=6, fy=60, Es=29000)

# plot PM interaction surface
fkit.plotter.plot_PM(section2, P=[50,400], M=[-500,3000])

```



## Documentation

[Link to Documentation](https://github.com/wcfrobert/fkit/tree/master/doc)


Alternatively, the user may access docstrings of any methods using the `help()` keyword in python:

```python
help(fkit.patchfiber.Hognestad)
fkit.patchfiber.Hognestad?
```

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/helpcommand.png?raw=true" alt="demo" style="width: 90%;" />
</div>


Here is a comprehensive list of all public methods available to the user. 

**Fiber Material Models**: [More Info](https://github.com/wcfrobert/fkit/tree/master/doc#fiber-material-models)

* `fkit.patchfiber.Hognestad(fpc, Ec="default", eo="default", emax=0.0038, alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray")`
* `fkit.patchfiber.Todeschini(fpc, Ec="default", eo="default", emax=0.0038, alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray")`
* `fkit.patchfiber.Mander(fpc, eo, emax, Ec="default", alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray")`
* `fkit.patchfiber.Bilinear(fy, fu, Es, ey="default", emax=0.1, default_color="black")`
* `fkit.patchfiber.Multilinear(fy, fu, Es, ey1="default", ey2=0.008, stress1=0.83, stress2=0.98, stress3=1.00, stress4=0.84, strain1=0.03, strain2=0.07, strain3=0.10, strain4=0.16, default_color="black")`
* `fkit.patchfiber.RambergOsgood(fy, Es, n, emax=0.16, default_color="black")`
* `fkit.patchfiber.MenegottoPinto(fy, Es, b, n, emax=0.16, default_color="black")`
* `fkit.patchfiber.Custom_Trilinear(strain1p, strain2p, strain3p, stress1p, stress2p, stress3p, strain1n="default", strain2n="default", strain3n="default", stress1n="default", stress2n="default", stress3n="default", default_color="black")`
* ~
* `fkit.nodefiber.Bilinear(fy, fu, Es, ey="default", emax=0.1, default_color="black")`
* `fkit.nodefiber.Multilinear(fy, fu, Es, ey1="default", ey2=0.008, stress1=0.83, stress2=0.98, stress3=1.00, stress4=0.84, strain1=0.03, strain2=0.07, strain3=0.10, strain4=0.16, default_color="black")`
* `fkit.nodefiber.RambergOsgood(fy, Es, n, emax=0.16, default_color="black")`
* `fkit.nodefiber.MenegottoPinto(fy, Es, b, n, emax=0.16, default_color="black")`
* `fkit.nodefiber.Custom_Trilinear(strain1p, strain2p, strain3p, stress1p, stress2p, stress3p, strain1n="default", strain2n="default", strain3n="default", stress1n="default", stress2n="default", stress3n="default", default_color="black")`



**Section Definition**: [More Info](https://github.com/wcfrobert/fkit/tree/master/doc#manual-section-creation)

* `fkit.section.Section.add_patch(xo, yo, b, h, nx, ny, fiber)`
* `fkit.section.Section.add_bar_group(xo, yo, b, h, nx, ny, area, perimeter_only, fiber)`
* `fkit.section.Section.add_bar(coord, area, fiber)`
* `fkit.section.Section.mesh(rotate=0)`



**SectionBuilder**: [More Info](https://github.com/wcfrobert/fkit/tree/master/doc#sectionbuilder)

* `fkit.sectionbuilder.rectangular(width, height, cover, top_bar, bot_bar, concrete_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)`
* `fkit.sectionbuilder.rectangular_confined(width, height, cover, top_bar, bot_bar, core_fiber, cover_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)`
* `fkit.sectionbuilder.circular(diameter, cover, N_bar, A_bar, core_fiber, cover_fiber, steel_fiber, mesh_n=0.5)`
* `fkit.sectionbuilder.flanged(bw, bf, h, tf, cover, bot_bar, top_bar, slab_bar, core_fiber, cover_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)`
* `fkit.sectionbuilder.wall(width, length, cover, wall_bar, concrete_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)`
* `fkit.sectionbuilder.wall_BE(width, length, cover, BE_length, wall_bar, BE_bar, concrete_fiber, BE_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)`
* `fkit.sectionbuilder.wall_layered(width1, width2, length, cover, wall_bar1, wall_bar2, concrete_fiber1, concrete_fiber2, steel_fiber1, steel_fiber2, mesh_nx=0.5, mesh_ny=0.5)`
* `fkit.sectionbuilder.wall_speedcore(length, width, steel_thickness, concrete_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)`
* `fkit.sectionbuilder.wide_flange(bf, d, tw, tf, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)`
* `fkit.sectionbuilder.W_AISC(shape, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)`



**Analysis commands**: [More Info](https://github.com/wcfrobert/fkit/tree/master/doc#moment-curvature-analysis)

* `fkit.section.Section.run_moment_curvature(phi_target, P=0, N_step=100, show_progress=False)`
* `fkit.section.Section.calculate_Icr(Es, Ec)`
* `fkit.section.Section.run_PM_interaction(fpc, fy, Es)`
* `fkit.section.Section.get_node_fiber_data(tag)`
* `fkit.section.Section.get_patch_fiber_data(location)`
* `fkit.section.Section.get_all_fiber_data()`
* `fkit.section.Section.export_data(save_folder="fkit_result_folder")`



**Visualizations**: [More Info](https://github.com/wcfrobert/fkit/tree/master/doc#visualization)

* `fkit.plotter.preview_fiber(fiber, xlim=[-0.03, 0.03])`
* `fkit.plotter.preview_section(section, show_tag=False)`
* `fkit.plotter.plot_MK(section)`
* `fkit.plotter.animate_MK(section)`
* `fkit.plotter.plot_Icr(section)`
* `fkit.plotter.plot_PM(section, P=None, M=None)`





## Notes and Assumptions

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/signconvention.png?raw=true" alt="demo" style="width: 45%;" />
</div>



* Sign conventions: 
  * +ve is tensile stress/strain, 
  * -ve is compressive stress/strain
* Please ensure consistent unit input:
  * SI Unit: **(N, mm, MPa)**
  * Imperial Unit: **(kips, in, ksi)**
* Moment curvature analysis is code-agnostic. On the other hand, the PM interaction analysis is **for reinforced concrete sections only** and follows ACI 318-19 assumptions (e.g. rectangular stress block, elastic-perfect-plastic steel, spalling strain of 0.003, etc). Solution is independent of user-specified fiber materials as all concrete fibesr are converted to exhibit rectangular stress block behavior, and all rebar fibers are converted to elastic-perfect-plastic behavior.
* Disclaimer: this is not enterprise-grade software. Please do NOT use it for work. Users assume full risk and responsibility for verifying that the results are accurate.




## License

MIT License

Copyright (c) 2023 Robert Wang
