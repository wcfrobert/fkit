<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/logo.png?raw=true" alt="logo" style="zoom:50%;" />
  <br>
  Fiber Section Analysis in Python
  <br>
</h1>
<p align="center">
Define fiber stress-strain relationships -> Create section -> Perform moment-curvature and PM interaction analysis with ease.
</p>




<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 100%;" />
</div>


- [1.0 Introduction](#10-introduction)
- [2.0 Quick Start](#20-quick-start)
- [3.0 Installation](#30-installation)
- [4.0 Usage](#40-usage)
- [5.0 Fiber Stress-Strain Models](#50-fiber-stress-strain-models)
- [6.0 Section Object](#60-section-object)
- [7.0 SectionBuilder Templates](#70-sectionbuilder-templates)
- [8.0 Visualization Options](#80-visualization-options)
- [9.0 Notes and Assumptions](#90-notes-and-assumptions)
- [License](#license)
- [APPENDIX: Theoretical Background Moment Curvature](#appendix--theoretical-background-moment-curvature)
- [APPENDIX: Theoretical Background P+M Interaction Surface](#appendix--theoretical-background-p-m-interaction-surface)
- [APPENDIX: Validation Problem](#appendix--validation-problem)





## 1.0 Introduction

fkit (fiber-kit) is a section analysis program implemented in Python that is incredibly powerful, flexible, and easy to use. Perform **moment-curvature** and **P+M interaction** analysis with very few lines of code. Originally meant for reinforced concrete sections, it was later extended to all material type (e.g. wood, steel, FRPs, anything that can be defined by a stress-strain curve). 

Notable Features:

* Large selection of material models (Hognestad, Mander, Todeschini, Ramberg-Osgood, Menegotto-Pinto, etc)
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






## 2.0 Quick Start

**Installation**

See "Installation" section below for more info. For casual users, use Anaconda Python, download this module, and run Spyder IDE.

**Quick Start Script**

Run main_quickstart.py:

```python
# import fkit
import fkit
from fkit.plotter import plot_MK, plot_PM
from fkit.patchfiber import Hognestad
from fkit.nodefiber import Bilinear

# define fibers
fiber_concrete = Hognestad(fpc=5, take_tension=True)
fiber_steel    = Bilinear(fy=60, Es=29000)

# Most common sections can be defined with SectionBuilder
section1 = fkit.sectionbuilder.rectangular(width = 24, height = 24, cover = 1.5,
                                           top_bar = [0.6, 2, 1, 0],
                                           bot_bar = [0.6, 4, 2, 3],
                                           concrete_fiber = fiber_concrete,
                                           steel_fiber = fiber_steel)

# moment curvature
section1.run_moment_curvature(phi_target=0.0003)

# P+M interaction
section1.run_interaction(fpc=5, fy=60, Es=29000)

# plot results
plot_MK(section1)
plot_PM(section1)

# export results to csv
section1.export_data()
```

Three other sample scripts are provided to help get the users up and running:

* `main_full.py` - illustrates all the major functionalities of fkit
* `main_notebook.ipynb` - for users more accustomed to notebook environments
* `main_fiber.py` - for testing out various fiber material definitions

Please note that fkit is agnostic when it comes to units. The above example script uses US imperial unit (kips, in, ksi). You may also use SI units (N, mm, MPa). Just make sure your unit input is consistent.

`plot_MK()` and `plot_PM()` produces the visualizations below. `export_data()` generates a result folder in the current working directory.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo2.png?raw=true" alt="demo" style="width: 60%;" />
</div>





## 3.0 Installation

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



## 4.0 Usage

Performing sophisticated section analyses with fkit is easy and can be broken down into 4 steps:

1. Define fibers material properties
2. Define section and mesh with previously defined fibers
3. Run moment curvature or PM interaction analysis
4. Visualize

Here is a sample script that illustrates most of the functionalities of fkit.

```python
import fkit

"""
#########################################
Step 1: Define fibers
#########################################
"""
# define fiber material properties
fiber_unconfined = fkit.patchfiber.Todeschini(fpc=5)
fiber_confined   = fkit.patchfiber.Mander(fpc=6, eo=0.004, emax=0.014)
fiber_steel      = fkit.nodefiber.Bilinear(fy=60, Es=29000)

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

# finalize geometry. The user also has the ability to rotate the section
section1.mesh(rotate=45)

# alternatively, most common sections can be quickly defined with SectionBuilder
# let's define the section above again
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
section2.run_moment_curvature(P=-180, phi_target=0.002)

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
# generate PM interaction surface
section2.run_interaction(fpc=6, fy=60, Es=29000)

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

In addition to the documentation provided herein, the user may access docstrings of all methods to get more help:

```python
help(fkit.patchfiber.Hognestad)
fkit.patchfiber.Hognestad?
```

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/helpcommand.png?raw=true" alt="demo" style="width: 90%;" />
</div>



Here is a comprehensive list of all the commands that is available to the user. 

**Defining material properties (Section 5.0 of README)**

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



**Defining sections manually (Section 6.0 of README)**

* `fkit.section.add_patch()`
* `fkit.section.add_bar_group()`
* `fkit.section.add_bar()`
* `fkit.section.mesh()`



**Defining sections with SectionBuilder (Section 7.0 of README)**

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



**Section analysis commands (Section 6.0 of README)**

* `fkit.section.run_moment_curvature()`
* `fkit.section.run_interaction()`
* `fkit.section.get_node_fiber_data()`
* `fkit.section.get_patch_fiber_data()`
* `fkit.section.export_data()`



**Visualization (Section 8.0 of README)**

* `fkit.plotter.preview_fiber()`
* `fkit.plotter.preview_section()`
* `fkit.plotter.plot_MK()`
* `fkit.plotter.animate_MK()`
* `fkit.plotter.plot_PM()`




## 5.0 Fiber Material Models

Two types of fibers are available. The difference between patch fibers and node fibers are as follows:

* **Patch fibers** are mainly used for concrete (but not always). A patch fiber has 4 vertices and occupies some area geometrically which is calculated internally. 
* **Node fibers** are always used for rebar. A node fiber is defined by a centroidal coordinate (a single point) and do not occupy any physical space. Instead, it is assigned a user-specified area.

There are currently 7 material models available in fkit.

* **Hognestad et al (1951)** - General purpose concrete
  
* **Mander et al (1988)** - Recommended for confined concrete
  
* **Todeschini et al (1964)** - Recommended for unconfined concrete
  
* **Bilinear** - Simple bilinear model
  
* **Multilinear: Rex & Easterling (1996)**  - Six linear regions tracing out the recognizable steel stress-strain curve
  
* **RambergOsgood** - Smooth power function. Often used to fit experimental data
  
* **MenegottoPinto** - Smooth power function. Slightly faster and more robust than RambergOsgood as no Newton-Raphson iteration is needed
  
* **Custom_Trilinear** - A highly customizable trilinear model defined by three points


Note that all input arguments are positive (+)



### 5.1 Hognestad

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/hognestad.png?raw=true" alt="demo" style="width: 60%;" />
</div>

`fkit.patchfiber.Hognestad(fpc, Ec="default", eo="default", emax=0.0038, alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray", vertices=None)` 

* fpc: float
  * Concrete cylinder strength. Peak stress will occur at 0.9fpc
  * The 10% reduction accounts for difference between cylinder strength and member strength 
* Ec: float (OPTIONAL)
  * Concrete modulus of elasticity
  * Default = If not specified, Ec will be calculated internally
    * If fpc > 15, assume unit is Mpa and Ec = 4700 * sqrt(fpc)
    * if fpc <= 15, assume unit is ksi and Ec = 57000 * sqrt(fpc*1000) / 1000 
* eo: float (OPTIONAL)
  * Strain at peak stress (fo=0.9fpc)
  * eo can range from 0.002 for unconfined concrete to 0.01 for confined concrete
  * Default = If not specified, eo will be calculated internally: eo = 1.8(fo)/Ec
* emax: float (OPTIONAL)
  * Maximum strain. Also known as ultimate or spalling strain
  * The value of emax ranges from 0.003 to 0.008 for unconfined concrete and can be as high as 0.04 for confined concrete
  * Default = 0.0038
* alpha: float (OPTIONAL)
  * Residual stress after max strain is exceeded. As percentage of fpc
  * Default = 0
* take_tension: boolean (OPTIONAL)
  * Boolean to consider concrete in tension
  * Default = False
* fr: float (OPTIONAL)
  * Modulus of rupture (tensile strength of concrete). Only active if take_tension = True
  * Default = If not specified, eo will be calculated internally
    * If fpc > 15, assume unit is Mpa and Ec = 0.62 * sqrt(fpc)
    * if fpc <= 15, assume unit is ksi and Ec = 7.5 * sqrt(fpc*1000) / 1000 
* er: float (OPTIONAL)
  * Strain at modulus of rupture.  Only active if take_tension = True
  * Default = 0.00015
* default_color: string (OPTIONAL)
  * specify a fiber color. List of matplotlib named color: https://matplotlib.org/stable/gallery/color/named_colors.html
  * Default = "lightgray"

```python
# Hognestad unconfined
unconfined = patchfiber.Hognestad(fpc=5)

# Hognestad confined
confined = patchfiber.Hognestad(fpc=6, eo=0.004, emax=0.014)

# Note that all input arguments are positive!
# For more guidance on eo and emax which varies based on degree of confinement:
#     A. Wight & MacGregor (2012). Reinforced Concrete Mechanics & Design 6E.
#     B. Moehle (2014). Seismic Design of Reinforced Concrete Buildings
```



### 5.2 Todeschini

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/todeschini.png?raw=true" alt="demo" style="width: 60%;" />
</div>

`fkit.patchfiber.Todeschini(fpc, Ec="default", eo="default", emax=0.0038, alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray", vertices=None)` 

* fpc: float
  * Concrete cylinder strength. Peak stress will occur at 0.9fpc
  * The 10% reduction accounts for difference between cylinder strength and member strength 
* Ec: float (OPTIONAL)
  * Concrete modulus of elasticity
  * Default = If not specified, Ec will be calculated internally
    * If fpc > 15, assume unit is Mpa and Ec = 4700 * sqrt(fpc)
    * if fpc <= 15, assume unit is ksi and Ec = 57000 * sqrt(fpc*1000) / 1000 
* eo: float (OPTIONAL)
  * Strain at peak stress (fo=0.9fpc)
  * eo can range from 0.002 for unconfined concrete to 0.01 for confined concrete
  * Default = If not specified, eo will be calculated internally: eo = 1.71(fo)/Ec
* emax: float (OPTIONAL)
  * Maximum strain. Also known as ultimate or spalling strain
  * The value of emax ranges from 0.003 to 0.008 for unconfined concrete and can be as high as 0.04 for confined concrete
  * Default = 0.0038
* alpha: float (OPTIONAL)
  * Residual stress after max strain is exceeded. As percentage of fpc
  * Default = 0
* take_tension: boolean (OPTIONAL)
  * Boolean to consider concrete in tension
  * Default = False
* fr: float (OPTIONAL)
  * Modulus of rupture (tensile strength of concrete). Only active if take_tension = True
  * Default = If not specified, eo will be calculated internally
    * If fpc > 15, assume unit is Mpa and Ec = 0.62 * sqrt(fpc)
    * if fpc <= 15, assume unit is ksi and Ec = 7.5 * sqrt(fpc*1000) / 1000 
* er: float (OPTIONAL)
  * Strain at modulus of rupture.  Only active if take_tension = True
  * Default = 0.00015
* default_color: string (OPTIONAL)
  * specify a fiber color. List of matplotlib named color: https://matplotlib.org/stable/gallery/color/named_colors.html
  * Default = "lightgray"

```python
# Todeschini is only recommended for unconfined concrete
unconfined = patchfiber.Todeschini(fpc=5)
```





### 5.3 Mander

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/mander.png?raw=true" alt="demo" style="width: 60%;" />
</div>



`fkit.patchfiber.Mander(fpc, eo, emax, Ec="default", alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray", vertices=None)` 

* fpc: float
  * Concrete cylinder strength (peak stress = fo = fpc)
* eo: float
  * Strain at peak stress
  * eo can range from 0.002 for unconfined concrete to 0.01 for confined concrete
* emax: float
  * Maximum strain. Also known as ultimate or spalling strain
  * The value of emax ranges from 0.003 to 0.008 for unconfined concrete and can be as high as 0.04 for confined concrete
* Ec: float (OPTIONAL)
  * Concrete modulus of elasticity
  * Default = If not specified, Ec will be calculated internally
    * If fpc > 15, assume unit is Mpa and Ec = 4700 * sqrt(fpc)
    * if fpc <= 15, assume unit is ksi and Ec = 57000 * sqrt(fpc*1000) / 1000 
* alpha: float (OPTIONAL)
  * Residual stress after max strain is exceeded. As percentage of fpc
  * Default = 0
* take_tension: boolean (OPTIONAL)
  * Boolean to consider concrete in tension
  * Default = False
* fr: float (OPTIONAL)
  * Modulus of rupture (tensile strength of concrete). Only active if take_tension = True
  * Default = If not specified, eo will be calculated internally
    * If fpc > 15, assume unit is Mpa and Ec = 0.62 * sqrt(fpc)
    * if fpc <= 15, assume unit is ksi and Ec = 7.5 * sqrt(fpc*1000) / 1000 
* er: float (OPTIONAL)
  * Strain at modulus of rupture.  Only active if take_tension = True
  * Default = 0.00015
* default_color: string (OPTIONAL)
  * specify a fiber color. List of matplotlib named color: https://matplotlib.org/stable/gallery/color/named_colors.html
  * Default = "lightgray"

```python
# Mander unconfined
unconfined = patchfiber.Mander(fpc=5, eo=0.002, emax=0.0038)

# Mander confined
confined = patchfiber.Mander(fpc=6, eo=0.004, emax=0.014)

# Note that all input arguments are positive!
# For more guidance on eo and emax which varies based on degree of confinement:
#     A. Wight & MacGregor (2012). Reinforced Concrete Mechanics & Design 6E.
#     B. Moehle (2014). Seismic Design of Reinforced Concrete Buildings
```





### 5.4 Bilinear

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/bilinear.png?raw=true" alt="demo" style="width: 60%;" />
</div>



`fkit.nodefiber.Bilinear(fy, fu, Es, ey="default", emax=0.1, default_color="black", coord=None, area=None)`

* fy: float
  * Yield stress

* Es: float
  * Elastic modulus

* fu: float (OPTIONAL)
  * Ultimate stress
  * Default = fy
  
* ey: float (OPTIONAL)
  * Yield strain
  * Default = fy / Es

* emax: float (OPTIONAL)
  * Maximum strain. Stress = 0 if exceeded.
  * Default = 0.1

* default_color: string (OPTIONAL)
  * specify a fiber color. List of matplotlib named color: https://matplotlib.org/stable/gallery/color/named_colors.html
  * Default = "black"


```python
# Elastic Perfect Plastic (EPP) model
fiber1 = nodefiber.Bilinear(fy=60, fu=60, Es=29000)

# Strain Hardening
fiber2 = nodefiber.Bilinear(fy=60, fu=90, Es=29000)

# Strain Softening
fiber3 = nodefiber.Bilinear(fy=60, fu=30, Es=29000)

# For Bilinear *Patch* Fibers
patch = patchfiber.Bilinear(fy=50, fu=65, Es=29000)
```





### 5.5 Multilinear

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/multilinear.png?raw=true" alt="demo" style="width: 60%;" />
</div>



`fkit.nodefiber.Multilinear(fy, fu, Es, ey1="default", ey2=0.008, stress1=0.83, stress2=0.98, stress3=1.00, stress4=0.84, strain1=0.03, strain2=0.07, strain3=0.10, strain4=0.16, default_color="black", coord=None, area=None)`

* fy: float
  * Yield stress
* Es: float
  * Elastic modulus
* fu: float
  * Ultimate stress
* ey1: float (OPTIONAL)
  * Strain at beginning of yield plateau
  * Default = fy / Es

* ey2: float (OPTIONAL)
  * Strain at end of yield plateau
  * Rex & Easterling (1996) recommends 0.008 for rebar, 0.02 for mild steel
  * Default = 0.008

* stress1: float (OPTIONAL)
  * Stress control point 1 (as a percentage of Fu)
  * Rex & Easterling (1996) recommends 0.85 for rebar, 0.83 for mild steel
  * Default = 0.83

* stress2: float (OPTIONAL)
  * Stress control point 2 (as a percentage of Fu)
  * Rex & Easterling (1996) recommends 0.98 for rebar, 0.95 for mild steel
  * Default = 0.98

* stress3: float (OPTIONAL)
  * Stress control point 3 (peak stress = Fu)
  * Default = 1.00

* stress4: float (OPTIONAL)
  * Stress control point 4 (as a percentage of Fu)
  * Rex & Easterling (1996) recommends 0.84 for rebar, 0.83 for mild steel
  * Default = 0.84

* strain1: float (OPTIONAL)
  * Strain control point 1
  * Rex & Easterling (1996) recommends 0.03 for rebar, 0.05 for mild steel
  * Default = 0.03

* strain2: float (OPTIONAL)
  * Strain control point 2
  * Rex & Easterling (1996) recommends 0.07 for rebar, 0.10 for mild steel  
  * Default = 0.07

* strain3: float (OPTIONAL)
  * Strain control point 3
  * Rex & Easterling (1996) recommends 0.10 for rebar, 0.20 for mild steel   
  * Default = 0.10

* strain4: float (OPTIONAL)
  * Strain control point 4 = emax
  * Rex & Easterling (1996) recommends 0.16 for rebar, 0.30 for mild steel
  * Default = 0.16


* default_color: string (OPTIONAL)
  * Specify a fiber color. List of matplotlib named color: https://matplotlib.org/stable/gallery/color/named_colors.html
  * Default = "black"

```python
# The stress-strain control nodes are based on experiments performed by Rex & Easterling (1996)

# It is very important to note that experimental data from coupon tests do not
# translate well to the member level behavior. There are a myriad of other factors 
# like bar slip, cyclic vs. static loading, and etc that must be considered for a truly # # "accurate" model. Use the default values with a grain of salt!

# Multilinear model
fiber1 = nodefiber.Multilinear(fy=60, fu=90, Es=29000)

# For Multilinear *Patch* Fibers
fiber2 = patchfiber.Bilinear(fy=50, fu=65, Es=29000,
                            ey2=0.02,
                            strain1=0.05, stress1=0.83,
                            strain2=0.10, stress2=0.95,
                            strain3=0.20, stress3=1.00,
                            strain4=0.30, stress4=0.83)
```





### 5.6 Custom Trilinear

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/customtrilinear.png?raw=true" alt="demo" style="width: 60%;" />
</div>



`fkit.nodefiber.Custom_Trilinear(strain1p, strain2p, strain3p, stress1p, stress2p, stress3p, strain1n="default", strain2n="default", strain3n="default", stress1n="default", stress2n="default", stress3n="default", default_color="black", coord=None, area=None)`

* strain1p: float

  * Strain control point 1 (tension side)

* strain2p: float

  * Strain control point 2 (tension side)

* strain3p: float

  * Strain control point 3 (tension side)

* stress1p: float

  * Stress control point 1 (tension side)

* stress2p: float

  * Stress control point 2 (tension side)

* stress3p: float

  * Stress control point 3 (tension side)

* strain1n: float (OPTIONAL)

  * Strain control point 1 (compression side)
  * Default = strain1p

* strain2n: float (OPTIONAL)

  * Strain control point 2 (compression side)
  * Default = strain2p

* strain3n: float (OPTIONAL)

  * Strain control point 3 (compression side)
  * Default = strain3p

* stress1n: float (OPTIONAL)

  * Stress control point 1 (compression side)
  * Default = stress1p

* stress2n: float (OPTIONAL)

  * Stress control point 2 (compression side)
  * Default = stress2p

* stress3n: float (OPTIONAL)

  * Stress control point 3 (compression side)
  * Default = stress3p

* default_color: string (OPTIONAL)

  * Specify a fiber color. List of matplotlib named color: https://matplotlib.org/stable/gallery/color/named_colors.html

  * Default = "black"

```python
# This is meant as a catch-all material type that is highly customizable

# Asymmetric Trilinear model
fiber1 = nodefiber.Custom_Trilinear(stress1p=75, strain1p=0.002,
                                	stress2p=100, strain2p=0.1,
                                	stress3p=75, strain3p=0.16,
                                	stress1n=-40, strain1n=-0.001,
                                	stress2n=-5, strain2n=-0.002,
                                	stress3n=-0, strain3n=-0.03)

# Trilinear *Patch* Fibers
patch = patchfiber.Custom_Trilinear(stress1p=75, strain1p=0.002,
                                	 stress2p=100, strain2p=0.1,
                                	 stress3p=75, strain3p=0.16)
```







### 5.7 RambergOsgood

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/RambergOsgood.png?raw=true" alt="demo" style="width: 60%;" />
</div>



`fkit.nodefiber.RambergOsgood(fy, Es, n, emax=0.16, default_color="black", coord=None, area=None)`

* fy: float

  * Yield stress

* Es: float

  * Elastic modulus

* n: float

  * RambergOsgood Parameter. Lower value = smoother curve.

* emax: float (OPTIONAL)

  * Maximum strain. Stress = 0 if exceeded.
  * Default = 0.16

* default_color: string (OPTIONAL)

  * Specify a fiber color. List of matplotlib named color: https://matplotlib.org/stable/gallery/color/named_colors.html

  * Default = "black"

```python
# RambergOsgood smooth power function for stress and strain
fiber1 = nodefiber.RambergOsgood(fy=60, Es=29000, n=25)

# RambergOsgood *Patch* Fibers
patch = patchfiber.RambergOsgood(fy=60, Es=29000, n=25)
```





### 5.8 Menegotto-Pinto

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/menegottopinto.png?raw=true" alt="demo" style="width: 60%;" />
</div>



`fkit.nodefiber.MenegottoPinto(fy, Es, b, n, emax=0.16, default_color="black", coord=None, area=None)`

* fy: float

  * Yield stress

* Es: float

  * Elastic modulus

* b: float

  * MenegottoPinto Parameter. Adjusts strain hardening slope.

* n: float

  * MenegottoPinto Parameter. Lower value = smoother curve.

* emax: float (OPTIONAL)

  * Maximum strain. Stress = 0 if exceeded.
  * Default = 0.16

* default_color: string (OPTIONAL)

  * Specify a fiber color. List of matplotlib named color: https://matplotlib.org/stable/gallery/color/named_colors.html

  * Default = "black"

```python
# MenegottoPinto smooth power function for stress and strain
fiber1 = nodefiber.MenegottoPinto(fy=60, Es=29000, b=0.003, n=6)

# MenegottoPinto *Patch* Fibers
patch = patchfiber.MenegottoPinto(fy=60, Es=29000, b=0.003, n=6)
```



## 6.0 Section Analysis Commands

### 6.1 Manual Section Creation 

`fkit.section.Section.add_patch(xo, yo, b, h, nx, ny, fiber)` - add a rectangular area of patch fibers

* xo: float
  * x coordinate of lower left corner
* yo: float
  * y coordinate of lower left corner
* b: float
  * width of patch area
* h: float
  * height of patch area
* nx: float
  * number of fibers along width
* ny: float
  * number of fibers along height
* fiber: fkit.patchfiber object
  * patch fiber object with user-defined material properties

```python
# add a rectangular section where 16" width, 20" height, with lower left corner
# located at (0,0), 5 patches along width, 20 patches along height, using a previously
# defined concrete fiber
section.add_patch(xo=0, yo=0, b=16, h=20, nx=5, ny=20, fiber=my_fiber)
```



`fkit.section.Section.add_bar(coord, area, fiber)` - add a single rebar at specified coordinate

* coord: [float, float]
  * (x,y) coordinate where node fiber will be added
* area: float
  * area of node fiber
* fiber: fkit.nodefiber object
  * node fiber object with user-defined material properties

```python
# add a rebar at (15, 25) with area of 0.6 in^2 using a prevoiusly defined steel fiber
section.add_bar(coord=[15,25], area=0.6, fiber=my_fiber)
```



`fkit.section.Section.add_bar_group(xo, yo, b, h, nx, ny, area, perimeter_only, fiber)` - add a rectangular array of rebar

* xo: float
  * x coordinate of bottom left corner
* yo: float
  * y coordinate of bottom left corner
* b: float
  * width of rebar group
* h: float
  * height of rebar group
* nx: float
  * number of rebar in x
* ny: float
  * number of rebar in y
* area: float
  * cross sectional area of rebar
* perimeter_only: boolean
  * flag for indicating having rebar on perimeter only or fill full array
* fiber: fkit.nodefiber object
  *  node fiber object with material properties



```python
# add 8 rebar along perimeter of a column. The column is 20"x20", we assume 1.5" cover
# which means the rectangular array is 17"x17". Each bar has area of 0.6 in^2
my_section.add_bar_group(xo=1.5, yo=1.5, 
                         b=17, h=17, 
                         nx=3, ny=3, 
                         perimeter_only=True, 
                         fiber=my_fiber)
```



`fkit.section.Section(rotate=0)` finish section creation and mesh.

* rotate: float (OPTIONAL)
  * rotate the section counter-clockwise by a user-specified angle (in degrees)
  * default = 0

```python
# finish section creation and rotate it 35 degrees
my_section.mesh(rotate=35)
```



### 6.2 Moment Curvature and PM Interaction Analysis

`fkit.section.Section.run_moment_curvature(phi_target, P=0, N_step=100, show_progress=False)` - start moment curvature analysis

* phi_target: float
  * target curvature which the analysis will attempt to progress to (i.e. how far to push the section)
  * It is difficult to specify a default value as curvature is unit dependent (i.e. 1/in vs. 1/mm). A good starting point is to estimate yield curvature as
    * phi_yield ~= ecu / (1-j)d ~= 0.003 / 0.25d
    * example: 24 in deep section => 0.003 / (0.25)24 = 5.0 e-4   1/in
    * example: 600 mm deep section => 0.003 / (0.25)600 = 2.0 e-5  1/mm
* P: float (OPTIONAL)
  * applied axial load (COMPRESSION IS NEGATIVE (-))
  * default = 0
* N_step: integer (OPTIONAL)
  * number of analysis steps to get to target curvature
  * default = 100
* show_progress: boolean (OPTIONAL)
  * flag to print result from each step
  * default = False
* RETURNS:
  * a dataframe containing all relevant analysis results

```python
# start moment curvature analysis with target curvature of 0.003 and applied axial load
# of 180 kips compression
MK_results = my_section.run_moment_curvature(phi_target=0.003, P=-180)

# Note:
# For asymmetric sections (including asymmetrically reinforced sections), 
# some minor-axis moment may develop. This is because orientation of neutral axis
# is not always equal to orientation of applied moment vector. As curvature increases,
# some minor-axis moment must develop to maintain equilibrium and to keep the 
# neutral-axis in the same user-specified orientation.
```



`fkit.section.Section.run_interaction(fpc, fy, Es)` - runs PM interaction analysis based on ACI 318-19. Note that PM interaction analysis is **fiber-independent**. In other words, the **fiber material properties defined earlier does not matter** as all concrete fibers are converted to exhibit rectangular stress-blocks behavior and all rebar converted to elastic-perfect-plastic.

* fpc: float
  * concrete cylinder strength
* fy: float
  * rebar yield strength
* Es: float
  * elastic modulus of rebar
* RETURNS:
  * a dataframe containing all relevant analysis results

```python
# generate PM interaction surface
PM_results = my_section.run_interaction(fpc=4, fy=60, Es=29000)

# returns a dictionary where key = orientaiton (from 0 to 360). Values are lists:
# "P", "Mx", "My", "c", "resistance factor", "P_factored", "Mx_factored", "My_factored"
```



### 6.3 Extracting Analysis Data

`fkit.section.Section.get_node_fiber_data(tag)` - returns moment curvature stress/strain history data of a node fiber.

* tag: int
  * node fiber ID. Use preview_section(show_tag=True) to see node fiber IDs
* RETURNS:
  * a dictionary of fiber data from moment curvature analysis

```python
# return rebar stress/strain history of node fiber 3
rebar3_data = my_section.get_node_fiber_data(tag=3)

# returns a dictionary with the following keys
# "coord" - coordinate of node fiber
# "depth" - depth of node fiber with respect to extreme compression fiber
# "ecc" - distance from section centroid to node fiber
# "stress" - stress history
# "strain" - strain history
# "force" - force contribution history 
# "momentx" - moment about x-axis contribution 
# "momenty" - moment about y-axis contribution 
```



`fkit.section.Section.get_patch_fiber_data(location)` - returns moment curvature stress/strain history data of a patch fiber.

* location: float or string
  * location can be "top", "bottom", or a coordinate list [x,y]
  * if "top", data from top-most fiber will be reported (max y)
  * if "bottom", data from bottom-most fiber will be reported (min y)
  * if a user-specified coordinate, the program will find the nearest fiber
* RETURNS:
  * a dictionary of fiber data from moment curvature analysis

```python
# retrieve data of fiber closest to coordinate (23,14)
fiber_data = my_section.get_patch_fiber_data(location=[23,14])
```



`fkit.section.Section.export_data(save_folder="exported_data_fkit")` - export data in csv format in a folder in current working directory. Three files will be generated "MK.csv", PM.csv", and "PM_factored.csv"

* save_folder: string
  * name of folder where csv file will be exported





## 7.0 SectionBuilder

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/sectionbuilder.png?raw=true" alt="demo" style="width: 100%;" />
</div>




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







## 8.0 Visualization

`fkit.plotter.preview_fiber(fiber, xlim=[-0.03, 0.03])` - show fiber stress-strain

* fiber: fkit.nodefiber object or fkit.patchfiber object
  * fiber object defined by user
* xlim: [float, float] (OPTIONAL)
  * lower and upper strain limit for plotting purposes
  * default = [-0.03, 0.03]



<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/previewfiber.png?raw=true" alt="demo" style="width: 60%;" />
</div>



`fkit.plotter.preview_section(section, show_tag=False)` - show section geometry

* section: fkit.section object
  * section object defined by user
* show_tag: boolean (OPTIONAL)
  * show rebar ID or not
  * default = False



<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/previewsection.png?raw=true" alt="demo" style="width: 30%;" />
</div>





`fkit.plotter.plot_MK(section)` - plot moment curvature analysis results

* section: fkit.section object
  * section object defined by user

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/plotmk.png?raw=true" alt="demo" style="width: 60%;" />
</div>



`fkit.plotter.animate_MK(section)` -  generate a folder in current working directory containing pngs which can be converted to gif externally

* section: fkit.section object
  * section object defined by user

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 60%;" />
</div>


`fkit.plotter.plot_PM(section, P=None, M=None)` - plot PM interaction surface

* section: fkit.section object
  * section object defined by user
* P: [float] (OPTIONAL)
  * list of axial demands for plotting
  * default = None

* M: [float] (OPTIONAL)
  * list of moment demands for plotting (same length as P)
  * default = None

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/plot_PM.png?raw=true" alt="demo" style="width: 60%;" />
</div>













## 9.0 Notes and Assumptions

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/signconvention.png?raw=true" alt="demo" style="width: 60%;" />
</div>


* Sign conventions: 
  * +ve is tensile stress/strain, 
  * -ve is compressive stress/strain
  * Major axis (x) points to the right
  * Minor axis (y) points up

* fkit is agnostic when it comes to unit. Please ensure consistent input.
  * SI Unit: N, mm, MPa
  * Freedom Unit: kips, in, ksi
* Node fibers and patch fibers often overlap. Within the compression region, this overlap of concrete and steel area results in some forces being double counted. For most lightly reinforced sections, the change to the final result is insignificant and we simplify the problem without any appreciable loss in accuracy by just ignoring this overlap. 






## 10.0 License

MIT License

Copyright (c) 2023 Robert Wang









## APPENDIX: Theoretical Background Moment Curvature

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/fbd.png?raw=true" alt="demo" style="width: 60%;" />
</div>

The figure above depicts state of stress where the external forces (highlighted green), and internal forces (highlighted yellow) are in equilibrium. Note that the strain profile is assumed linear; a fundamental assumption in section analysis known as plane-section-remain-plane.

$$\sum F = 0$$

$$\sum M = 0$$

A moment curvature analysis involves incrementally increasing curvature (shown as $$\phi$$ in the above diagram; sometimes the Greek letter $\kappa$ is also often used). At each step, a depth of neutral axis is determined in order to satisfy equilibrium. The process is displacement-based and can be thought of as increasingly bending a beam further and further. The figure below illustrates this process.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/momentcurvaturesteps.png?raw=true" alt="demo" style="width: 100%;" />
</div>

The moment curvature analysis algorithm is as follows:

1. Section is discretized into patch fibers and node fibers
2. Slowly increment curvature from 0 to an user-specified target ($\phi_{target}$)
3. At each curvature ($\phi$), use secant method to search for the depth of neutral axis that satisfies equilibrium. For a given neutral axis depth ($$c$$) and for each fiber i:
      * Calculate fiber depth with respect to top of section ($$d_i$$)
      * Calculate fiber strain based on NA depth and curvature ($$\varepsilon_i = \phi*(d_i - c)$$)
      * Calculate fiber stress based on fiber material properties ($$\sigma_i =f(\varepsilon_i)$$)
      * Calculate fiber force contribution ($$F_i = \sigma_i A_i$$)
        * ($$A_i$$) is fiber area
      * Calculate fiber moment contribution ($$M_i = F_i e_i$$)
        * ($$e_i$$) is the distance between fiber centroid to section centroid
        * ($$e_{ix} = x_{fiber} - x_{section}$$)
        * ($$e_{iy} = y_{fiber} - y_{section}$$)
4. Neural axis depth is found if force is in equilibrium (considering applied axial load):
      * $$\sum F_i - P = 0 $$

5. At the correct NA depth, sum moment about the section centroid
      * $$M = \sum M_i $$

6. Record this point ($$\phi, M$$) and move to next curvature increment, loop until reached $$\phi_{target}$$
                       



## APPENDIX: Theoretical Background P+M Interaction Surface

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/PMinteractionsteps.png?raw=true" alt="demo" style="width: 100%;" />
</div>

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/PMinteractionsteps2.png?raw=true" alt="demo" style="width: 100%;" />
</div>


## APPENDIX: Validation Problem





