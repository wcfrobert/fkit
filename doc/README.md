<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/logo.png?raw=true" alt="logo" style="zoom:50%;" />
  <br>
  Fiber Section Analysis in Python - Documentation
  <br>
</h1>





- [Analysis Commands](#analysis-commands)
  * [Manual Section Creation](#manual-section-creation)
  * [Moment Curvature Analysis](#moment-curvature-analysis)
  * [PM Interaction Analysis](#pm-interaction-analysis)
  * [Extracting Fiber Data](#extracting-fiber-data)
- [Visualization](#visualization)
- [Fiber Material Models](#fiber-material-models)
  * [Hognestad](#hognestad)
  * [Todeschini](#todeschini)
  * [Mander](#mander)
  * [Bilinear](#bilinear)
  * [Multilinear](#multilinear)
  * [Custom Trilinear](#custom-trilinear)
  * [RambergOsgood](#rambergosgood)
  * [Menegotto-Pinto](#menegotto-pinto)
- [SectionBuilder](#sectionbuilder)
  * [rectangular()](#rectangular--)
  * [rectangular_confined()](#rectangular-confined--)
  * [circular()](#circular--)
  * [flanged()](#flanged--)
  * [wall()](#wall--)
  * [wall_BE()](#wall-be--)
  * [wall_layered()](#wall-layered--)
  * [wide_flange()](#wide-flange--)
  * [W_AISC()](#w-aisc--)
  * [W_AISC_composite()](#w-aisc-composite--)
- [APPENDIX: Theoretical Background Moment Curvature](#appendix--theoretical-background-moment-curvature)
- [APPENDIX: Theoretical Background P+M Interaction Surface](#appendix--theoretical-background-p-m-interaction-surface)
- [APPENDIX: Validation Problem](#appendix--validation-problem)




## Analysis Commands

### Manual Section Creation 

`fkit.section.Section.add_patch(xo, yo, b, h, nx, ny, fiber)` - add patch fibers within a rectangular area

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
# add a rectangular section with 16" width, 20" height, with lower left corner
# located at (0,0), 5 patches along width, 20 patches along height
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
# add a rebar at (15, 25) with area of 0.6 in^2 
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
# which means the rectangular array is 17"x17". Each bar having an area of 0.6 in^2
my_section.add_bar_group(xo=1.5, yo=1.5, b=17, h=17, nx=3, ny=3, 
                         perimeter_only=True, 
                         fiber=my_fiber)
```



`fkit.section.Section(rotate=0)` finish section creation and mesh.

* rotate: float (OPTIONAL)
  * rotate the section counter-clockwise by a user-specified angle (in degrees)
  * default = 0

```python
# finish section creation and rotate it 35 degrees counter-clockwise
my_section.mesh(rotate=35)
```



### Moment Curvature Analysis

`fkit.section.Section.run_moment_curvature(phi_target, P=0, N_step=100, show_progress=False)` - start moment curvature analysis

* phi_target: float
  * target curvature which the analysis will attempt to progress to (i.e. how far to push the section)
  * It is difficult to specify a default value as curvature is unit dependent (i.e. 1/in vs. 1/mm). We can estimate yield curvature as follows assuming 0.003 crushing strain with a corresponding neutral axis depth of 0.25d
    * $\phi_{yield} = \frac{e_{cu}}{c} \approx \frac{0.003}{0.25d}$
    * example: 24 in deep section => $\phi_{target} = 0.003 / (0.25)24 = 5.0 \times 10^{-4}   \frac{1}{in}$
    * example: 600 mm deep section => $\phi_{target} = 0.003 / (0.25)600 = 2.0 \times 10^{-5}  \frac{1}{mm}$
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



### PM Interaction Analysis

`fkit.section.Section.run_PM_interaction(fpc, fy, Es)` - runs PM interaction analysis based on ACI 318-19. Note that PM interaction analysis is **fiber-independent**. In other words, the **fiber material properties defined earlier does not matter** as all concrete fibers are converted to exhibit rectangular stress-blocks behavior and all rebar converted to elastic-perfect-plastic.

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



### Extracting Fiber Data

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





## Visualization

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





## Fiber Material Models

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



### Hognestad

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



### Todeschini

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





### Mander

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





### Bilinear

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





### Multilinear

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





### Custom Trilinear

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







### RambergOsgood

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





### Menegotto-Pinto

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



## SectionBuilder

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/sectionbuilder.png?raw=true" alt="demo" style="width: 100%;" />
</div>


### rectangular()

### rectangular_confined()

### circular()

### flanged()

### wall()

### wall_BE()

### wall_layered()

### wide_flange()

### W_AISC()

### W_AISC_composite()



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





