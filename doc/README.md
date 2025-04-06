<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/logo.png?raw=true" alt="logo" style="zoom:50%;" />
  <br>
  Fiber Kit - Documentation
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




## Analysis Commands

### Manual Section Creation 

`fkit.section.Section()` - Instantiate and return a fiber kit section object.

```python
# instantiate a section object
import fkit
my_section = fkit.Section()
```

`fkit.section.Section.add_patch(xo, yo, b, h, nx, ny, fiber)` - Add patch fibers within a rectangular area. This method modifies the `Section` object internally and does not return anything.

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
my_section.add_patch(xo=0, yo=0, b=16, h=20, nx=5, ny=20, fiber=my_fiber)
```



`fkit.section.Section.add_bar(coord, area, fiber)` - Add a single rebar at specified (x, y) coordinate. This method modifies the `Section` object internally and does not return anything.

* coord: [float, float]
  * (x,y) coordinate where node fiber will be added
* area: float
  * area of node fiber
* fiber: fkit.nodefiber object
  * node fiber object with user-defined material properties

```python
# add a rebar at (15, 25) with area of 0.6 in^2 
my_section.add_bar(coord=[15,25], area=0.6, fiber=my_fiber)
```



`fkit.section.Section.add_bar_group(xo, yo, b, h, nx, ny, area, perimeter_only, fiber)` - Add a rectangular array of rebar. This method modifies the `Section` object internally and does not return anything.

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



`fkit.section.Section.mesh(rotate=0)` finish section creation and mesh. This method modifies the `Section` object internally and does not return anything.

* rotate: float (OPTIONAL)
  * rotate the section counter-clockwise by a user-specified angle (in degrees)
  * default = 0

```python
# finish section creation and rotate it 35 degrees counter-clockwise
my_section.mesh(rotate=35)
```



### Moment Curvature Analysis

`fkit.section.Section.run_moment_curvature(phi_target, P=0, N_step=100, show_progress=False)` - Run moment curvature analysis. Returns a dataframe of moment curvature results where each row is a load step.

* phi_target: float
  * target curvature which the analysis will attempt to progress to (i.e. how far to bend the section)
  * It is difficult to specify a default value as curvature is unit dependent (i.e. 1/in vs. 1/mm). We can estimate yield curvature by assuming 0.003 crushing strain with a corresponding neutral axis depth of 0.25d
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

```python
# moment curvature analysis 180 kips of axial compression
MK_results = my_section.run_moment_curvature(phi_target=0.003, P=-180)
```



### PM Interaction Analysis

`fkit.section.Section.run_PM_interaction(fpc, fy, Es)` - Run PM interaction analysis in accordance with assumptions within ACI 318-19. Note that PM interaction analysis is **fiber-independent**. In other words, the **fiber material properties defined earlier does not matter** as all concrete fibers are converted to exhibit rectangular stress-blocks behavior and all rebar converted to elastic-perfect-plastic. Returns a dataframe of (P, M) interaction curve coordinates

* fpc: float
  * concrete cylinder strength
* fy: float
  * rebar yield strength
* Es: float
  * elastic modulus of rebar

```python
# generate PM interaction surface
PM_results = my_section.run_interaction(fpc=4, fy=60, Es=29000)
```



### Extracting Fiber Data

`fkit.section.Section.get_node_fiber_data(tag)` - Return moment curvature stress/strain of a selected node fiber at each load step.

* tag: int
  * node fiber ID. Use preview_section(show_tag=True) to see node fiber IDs
* The returned dictionary have the following keys:
  * `...["area"]` - area assigned to node fiber
  * `...["coord"]` - coordinate of node fiber (x, y)
  * `...["depth"]` - depth of node fiber with respect to the topmost compression fiber
  * `...["ecc"]` - distance between fiber and section centroid (ex, ey)
  * `...["fiber type"]` - material model type (e.g. Hognestad, Mander, etc.)
  * `...["stress"]` - a list containing fiber stress for each load step
  * `...["strain"]` - a list containing fiber strain for each load step
  * `...["force"]` - a list containing fiber force contribution ($\sigma dA$) for each load step
  * `...["momentx"]` - a list containing fiber moment contribution about x axis ($\sigma dA \times e_y$) for each load step
  * `...["momenty"] `- a list containing fiber moment contribution about y axis ($\sigma dA \times e_x$) for each load step


```python
# return rebar stress/strain history of rebar with tag=3
rebar3_data = my_section.get_node_fiber_data(tag=3)
```



`fkit.section.Section.get_patch_fiber_data(location)` - Return moment curvature stress/strain data of a patch fiber at each load step.

* location: float or string
  * location can be "top", "bottom", or a coordinate list [x,y]
  * if "top", data from top-most fiber will be reported (max y)
  * if "bottom", data from bottom-most fiber will be reported (min y)
  * if a user-specified coordinate, the program will find the nearest fiber
* * The returned dictionary have the following keys:
    * `...["area"]` - area of patch fiber (x, y)
    * `...["centroid"]` - centroid of patch fiber (x, y)
    * `...["depth"]` - depth of node patch with respect to the topmost compression fiber
    * `...["ecc"]` - distance between fiber and section centroid (ex, ey)
    * `...["fiber type"]` - material model type (e.g. Hognestad, Mander, etc.)
    * `...["stress"]` - a list containing fiber stress for each load step
    * `...["strain"]` - a list containing fiber strain for each load step
    * `...["force"]` - a list containing fiber force contribution ($\sigma dA$) for each load step
    * `...["momentx"]` - a list containing fiber moment contribution about x axis ($\sigma dA \times e_y$) for each load step
    * `...["momenty"] `- a list containing fiber moment contribution about y axis ($\sigma dA \times e_x$) for each load step

```python
# retrieve stress/strain data of the exteme compression fiber
fiber_data = my_section.get_patch_fiber_data(location="top")

# retrieve stress/strain data of concrete fiber closest to (23.4, 14.2)
fiber_data = my_section.get_patch_fiber_data(location=[23.4, 14.2])
```



`fkit.section.Section.export_data(save_folder="exported_data_fkit")` - Export data in csv format in a save_folder which will be created in the user current working directory.

* save_folder: string (OPTIONAL)
  * name of folder where csv file will be exported
  * default = "exported_data_fkit"





## Visualization

`fkit.plotter.preview_fiber(fiber, xlim=[-0.03, 0.03])` - Plot fiber stress-strain relationship. Returns the generated matplotlib figure.

* fiber: fkit.NodeFiber object or fkit.PatchFiber object
  * fiber object defined by user
* xlim: [float, float] (OPTIONAL)
  * lower and upper strain limit for plotting purposes
  * default = [-0.03, 0.03]



<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/previewfiber.png?raw=true" alt="demo" style="width: 60%;" />
</div>




`fkit.plotter.preview_section(section, show_tag=False)` - Show section geometry. Returns the generated matplotlib figure.

* section: fkit.Section object
  * section object defined by user
* show_tag: boolean (OPTIONAL)
  * show rebar ID or not
  * default = False



<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/previewsection.png?raw=true" alt="demo" style="width: 30%;" />
</div>






`fkit.plotter.plot_MK(section)` - Plot moment curvature analysis results. Returns the generated matplotlib figure.

* section: fkit.Section object
  * section object defined by user

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo2.png?raw=true" alt="demo" style="width: 60%;" />
</div>




`fkit.plotter.animate_MK(section)` -  Generate a folder in the user's current working directory containing pngs of each load step. The pngs can then be stapled together to create a gif.

* section: fkit.Section object
  * section object defined by user

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 60%;" />
</div>


`fkit.plotter.plot_PM(section, P=None, M=None)` - Plot PM interaction surface. Returns the generated matplotlib figure.

* section: fkit.Section object
  * section object defined by user
* P: [float] (OPTIONAL)
  * list of axial demands for plotting
  * default = None

* M: [float] (OPTIONAL)
  * list of moment demands for plotting (same length as P)
  * default = None

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo3.png?raw=true" alt="demo" style="width: 60%;" />
</div>






## Fiber Material Models

Two types of fibers are available. The difference between patch fibers and node fibers are as follows:

* **Patch** fibers are mainly used for concrete (but not always). A patch fiber has 4 vertices and occupies some area geometrically.
* **Node** fibers are always used for rebar. A node fiber is defined by a centroidal coordinate (a single point) and does not have an area. Instead, the user must specify its area.

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
`fkit.patchfiber.Hognestad(fpc, Ec="default", eo="default", emax=0.0038, alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray")` 

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
unconfined = fkit.patchfiber.Hognestad(fpc=5)

# Hognestad confined
confined = fkit.patchfiber.Hognestad(fpc=6, eo=0.004, emax=0.014)

# Note that all input arguments are positive!
# For more guidance on eo and emax which varies based on degree of confinement:
#     A. Wight & MacGregor (2012). Reinforced Concrete Mechanics & Design 6E.
#     B. Moehle (2014). Seismic Design of Reinforced Concrete Buildings
```



### Todeschini

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/todeschini.png?raw=true" alt="demo" style="width: 60%;" />
</div>
`fkit.patchfiber.Todeschini(fpc, Ec="default", eo="default", emax=0.0038, alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray")` 

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
unconfined = fkit.patchfiber.Todeschini(fpc=5)
```





### Mander

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/mander.png?raw=true" alt="demo" style="width: 60%;" />
</div>


`fkit.patchfiber.Mander(fpc, eo, emax, Ec="default", alpha=0, take_tension=False, fr="default", er="default", default_color="lightgray")` 

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
unconfined = fkit.patchfiber.Mander(fpc=5, eo=0.002, emax=0.0038)

# Mander confined
confined = fkit.patchfiber.Mander(fpc=6, eo=0.004, emax=0.014)

# Note that all input arguments are positive!
# For more guidance on eo and emax which varies based on degree of confinement:
#     A. Wight & MacGregor (2012). Reinforced Concrete Mechanics & Design 6E.
#     B. Moehle (2014). Seismic Design of Reinforced Concrete Buildings
```





### Bilinear

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/bilinear.png?raw=true" alt="demo" style="width: 60%;" />
</div>


`fkit.nodefiber.Bilinear(fy, fu, Es, ey="default", emax=0.1, default_color="black")`

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
fiber1 = fkit.nodefiber.Bilinear(fy=60, fu=60, Es=29000)

# Strain Hardening
fiber2 = fkit.nodefiber.Bilinear(fy=60, fu=90, Es=29000)

# Strain Softening
fiber3 = fkit.nodefiber.Bilinear(fy=60, fu=30, Es=29000)

# For Bilinear *Patch* Fibers
patch = fkit.patchfiber.Bilinear(fy=50, fu=65, Es=29000)
```





### Multilinear

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/multilinear.png?raw=true" alt="demo" style="width: 60%;" />
</div>


`fkit.nodefiber.Multilinear(fy, fu, Es, ey1="default", ey2=0.008, stress1=0.83, stress2=0.98, stress3=1.00, stress4=0.84, strain1=0.03, strain2=0.07, strain3=0.10, strain4=0.16, default_color="black")`

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
# translate well to the member level behavior. There are a so many other factors at play
# like bar slip, cyclic vs. static loading. Use the default values with a grain of salt!

# Multilinear model
fiber1 = fkit.nodefiber.Multilinear(fy=60, fu=90, Es=29000)

# For Multilinear *Patch* Fibers
fiber2 = fkit.patchfiber.Bilinear(fy=50, fu=65, Es=29000,
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


`fkit.nodefiber.Custom_Trilinear(strain1p, strain2p, strain3p, stress1p, stress2p, stress3p, strain1n="default", strain2n="default", strain3n="default", stress1n="default", stress2n="default", stress3n="default", default_color="black")`

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
fiber1 = fkit.nodefiber.Custom_Trilinear(stress1p=75, strain1p=0.002,
                                	stress2p=100, strain2p=0.1,
                                	stress3p=75, strain3p=0.16,
                                	stress1n=-40, strain1n=-0.001,
                                	stress2n=-5, strain2n=-0.002,
                                	stress3n=-0, strain3n=-0.03)

# Trilinear *Patch* Fibers
patch = fkit.patchfiber.Custom_Trilinear(stress1p=75, strain1p=0.002,
                                	 stress2p=100, strain2p=0.1,
                                	 stress3p=75, strain3p=0.16)
```







### RambergOsgood

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/RambergOsgood.png?raw=true" alt="demo" style="width: 60%;" />
</div>


`fkit.nodefiber.RambergOsgood(fy, Es, n, emax=0.16, default_color="black")`

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
fiber1 = fkit.nodefiber.RambergOsgood(fy=60, Es=29000, n=25)

# RambergOsgood *Patch* Fibers
patch = fkit.patchfiber.RambergOsgood(fy=60, Es=29000, n=25)
```





### Menegotto-Pinto

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/menegottopinto.png?raw=true" alt="demo" style="width: 60%;" />
</div>


`fkit.nodefiber.MenegottoPinto(fy, Es, b, n, emax=0.16, default_color="black")`

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
fiber1 = fkit.nodefiber.MenegottoPinto(fy=60, Es=29000, b=0.003, n=6)

# MenegottoPinto *Patch* Fibers
patch = fkit.patchfiber.MenegottoPinto(fy=60, Es=29000, b=0.003, n=6)
```



## SectionBuilder

SectionBuilder is simply a collection of functions. Each function parametrically constructs a section that's commonly encountered. Some of these are shown below. Rather than defining a section patch by patch, rebar by rebar, a new section can be created with a single function call.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/sectionbuilder.png?raw=true" alt="demo" style="width: 50%;" />
</div>



### rectangular()

`fkit.sectionbuilder.rectangular(width, height, cover, top_bar, bot_bar, concrete_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)` returns a fully constructed `fkit.Section()` object.

* width: float
  * section width

* height: float
  * section height

* cover: float
  * cover to center of bar

* top_bar: [float]
  * bars in top layer [bar area, number across, layer, layer spacing]. Set to None for no rebar
  * example: [0.6, 3, 1, 0] = 3 bars across in one layer with 0.6 in^2 area in top layer

* bot_bar: [float]
  * bars in bottom layer [bar area, number across, layer, layer spacing]. Set to None for no rebar
  * example: [0.6, 4, 2, 3] = two rows of 4 bars (8 total) with 0.6 in^2 area separated by a vertical distance of 3 in

* concrete_fiber: patchfiber object
  * patch fiber object with material properties for concrete

* steel_fiber: nodefiber object
  * node fiber object with material properties for steel rebar

* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5

* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5


```python
# rectangular section
section1 = fkit.sectionbuilder.rectangular(width = 36,
                                           height = 12,
                                           cover = 1.5,
                                           top_bar = [0.3, 6, 1, 0],
                                           bot_bar = [0.3, 6, 1, 0],
                                           concrete_fiber = fiber_unconfined,
                                           steel_fiber = fiber_rebar)
```



### rectangular_confined()

`fkit.sectionbuilder.rectangular_confined(width, height, cover, top_bar, bot_bar, core_fiber, cover_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)` returns a fully constructed `fkit.Section()` object.

* width: float
  * section width
* height: float
  * section height
* cover: float
  * cover to center of bar
* top_bar: [float]
  * bars in top layer [bar area, number across, layer, layer spacing]. Set to None for no rebar
  * example: [0.6, 3, 1, 0] = 3 bars across in one layer with 0.6 in^2 area in top layer
* bot_bar: [float]
  * bars in bottom layer [bar area, number across, layer, layer spacing]. Set to None for no rebar
  * example: [0.6, 4, 2, 3] = two rows of 4 bars (8 total) with 0.6 in^2 area separated by a vertical distance of 3 in
* core_fiber: patchfiber object
  * patch fiber object with material properties for concrete inner core

* cover_fiber: patchfiber object
  * patch fiber object with material properties for concrete outer cover

* steel_fiber: nodefiber object
  * node fiber object with material properties for steel rebar

* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5
* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# rectangular section with a confined core
section2 = fkit.sectionbuilder.rectangular_confined(width = 15, 
                                    				height = 24, 
                                    				cover = 1.5, 
                                    				top_bar = [0.6, 3, 1, 0], 
                                    				bot_bar = [0.6, 3, 2, 3], 
                                    				core_fiber = fiber_confined, 
                                    				cover_fiber = fiber_unconfined, 
                                    				steel_fiber = fiber_rebar)
```



### circular()

`fkit.sectionbuilder.circular(diameter, cover, N_bar, A_bar, core_fiber, cover_fiber, steel_fiber, mesh_n=0.5)` returns a fully constructed `fkit.Section()` object.

* diameter: float
  * section diameter

* cover: float
  * cover to bar center

* N_bar: int
  * number of rebar along perimeter

* A_bar: float
  * rebar area

* core_fiber: patchfiber object
  * patch fiber object with material properties for concrete inner core
* cover_fiber: patchfiber object
  * patch fiber object with material properties for concrete outer cover
* steel_fiber: nodefiber object
  * node fiber object with material properties for steel rebar
* mesh_n: float (OPTIONAL)
  * mesh density (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# circular section
section3 = fkit.sectionbuilder.circular(diameter = 36,
                        				cover = 2,
                        				N_bar = 6,
                        				A_bar = 1.0,
                        				core_fiber = fiber_confined, 
                        				cover_fiber = fiber_unconfined, 
                        				steel_fiber = fiber_rebar)
```



### flanged()

`fkit.sectionbuilder.flanged(bw, bf, h, tf, cover, bot_bar, top_bar, slab_bar, core_fiber, cover_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)` returns a fully constructed `fkit.Section()` object.

* bw: float
  * beam web width

* bf: float
  * beam flange width

* h: float
  * total section height (beam + slab)

* tf: float
  * slab thickness

* cover: float
  * cover to bar center

* top_bar: [float]
  * bars in top layer [bar area, number across, layer, layer spacing]. Set to None for no rebar
  * example: [0.6, 3, 1, 0] = 3 bars across in one layer with 0.6 in^2 area in top layer
* bot_bar: [float]
  * bars in bottom layer [bar area, number across, layer, layer spacing]. Set to None for no rebar
  * example: [0.6, 4, 2, 3] = two rows of 4 bars (8 total) with 0.6 in^2 area separated by a vertical distance of 3 in
* slab_bar: [float]
  * bars in slab [bar area, spacing between bar, layers, spacing between layer]. Set to None for no rebar
  * example: [0.6, 12, 2, 8] = two rows of bars separated by vertical spacing of 8 in. Bars are spaced at 12 in on center.

* core_fiber: patchfiber object
  * patch fiber object with material properties for concrete inner core
* cover_fiber: patchfiber object
  * patch fiber object with material properties for concrete outer cover
* steel_fiber: nodefiber object
  * node fiber object with material properties for steel rebar
* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5
* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# beam with an effective flange forming a T
section4 = fkit.sectionbuilder.flanged(bw = 24,
                                       bf = 120,
                        			   h = 48,
                                       tf = 12,
                                       cover = 2,
                                       bot_bar = [0.6, 4, 1, 0],
                                       top_bar = [0.6, 2, 1, 0],
                                       slab_bar = [0.2, 12, 2, 9],
                                       core_fiber = fiber_confined, 
                                       cover_fiber = fiber_unconfined, 
                                       steel_fiber = fiber_rebar)
```



### wall()

`fkit.sectionbuilder.wall(width, length, cover, wall_bar, concrete_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)` returns a fully constructed `fkit.Section()` object.

* width: float
  * wall thickness

* length: float
  * wall length

* cover: float
  * cover to bar center

* wall_bar: [float]
  * bars in wall [bar area, spacing between bar, layers]. Set to None for no rebar
  * example: [0.6, 12, 2] = 0.6 area bars spaced at 12 inches in two layers
* concrete_fiber: patchfiber object
  * patch fiber object with material properties for concrete
* steel_fiber: nodefiber object
  * node fiber object with material properties for steel rebar
* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5
* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# simple wall section without boundary elements
section5 = fkit.sectionbuilder.wall(width=12,
                    				length=120, 
                    				cover=1.5, 
                    				wall_bar=[0.31, 12, 2],
                    				concrete_fiber = fiber_unconfined,
                    				steel_fiber = fiber_rebar)
```



### wall_BE()

`fkit.sectionbuilder.wall_BE(width, length, cover, BE_length, wall_bar, BE_bar, concrete_fiber, BE_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5) `returns a fully constructed `fkit.Section()` object.

* width: float
  * wall thickness
* length: float
  * wall length
* cover: float
  * cover to bar center
* BE_length: float
  * length of boundary element

* wall_bar: [float]
  * bars in wall [bar area, spacing between bar, layers]. Set to None for no rebar
  * example: [0.6, 12, 2] = 0.6 area bars spaced at 12 inches in two layers
* BE_bar: [float]
  * rebar within boundary element [bar_area, nx, ny]. Set to None for no BE rebar
  * example: [0.6, 3, 4] = 0.6 in^2 area bars forming a rectangular array nx by ny within boundary element

* concrete_fiber: patchfiber object
  * patch fiber object with material properties for concrete wall
* BE_fiber: patchfiber object
  * patch fiber object with material properties for concrete boundary element confined

* steel_fiber: nodefiber object
  * node fiber object with material properties for steel rebar
* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5
* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# wall section with boundary elements on either end
section6 = fkit.sectionbuilder.wall_BE(width = 18, 
                                       length = 160, 
                                       cover = 2, 
                                       BE_length = 24, 
                                       wall_bar = [0.31, 6, 2], 
                                       BE_bar = [1.0, 3, 4],
                                       concrete_fiber = fiber_unconfined, 
                                       BE_fiber = fiber_confined, 
                                       steel_fiber = fiber_rebar)
```





### wall_layered()

`fkit.sectionbuilder.wall_layered(width1, width2, length, cover, wall_bar1, wall_bar2, concrete_fiber1, concrete_fiber2, steel_fiber1, steel_fiber2, mesh_nx=0.5, mesh_ny=0.5)` returns a fully constructed `fkit.Section()` object.

* width1: float
  * wall 1 thickness

* width2: float
  * wall 2 thickness

* length:float
  * wall length

* cover: float
  * cover to bar center

* wall_bar1: [float]
  * bars in wall 1 [bar area, spacing between bar, layers]. Set to None for no rebar
  * example: [0.6, 12, 2] = 0.6 area bars spaced at 12 inches in two layers
* wall_bar2: [float]
  * bars in wall 2 [bar area, spacing between bar, layers]. Set to None for no rebar
  * example: [0.6, 12, 2] = 0.6 area bars spaced at 12 inches in two layers
* concrete_fiber1: patchfiber object
  * patch fiber object with material properties for concrete in wall 1
* concrete_fiber2: patchfiber object
  * patch fiber object with material properties for concrete in wall 2
* steel_fiber1: nodefiber object
  * node fiber object with material properties for steel rebar in wall 1
* steel_fiber2: nodefiber object
  * node fiber object with material properties for steel rebar in wall 2
* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5
* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# layered wall section (meant to model shotcrete retrofits)
section7 = fkit.sectionbuilder.wall_layered(width1 = 6, 
                                            width2 = 12, 
                                            length = 120, 
                                            cover = 1.5, 
                                            wall_bar1 = [0.2, 12, 2], 
                                            wall_bar2 = [0.6, 6, 2],
                                            concrete_fiber1 = fiber_unconfined, 
                                            concrete_fiber2 = fiber_confined, 
                                            steel_fiber1 = fiber_rebar, 
                                            steel_fiber2 = fiber_rebar)
```





### wall_speedcore()

`fkit.sectionbuilder.wall_speedcore(length, width, steel_thickness, concrete_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)` returns a fully constructed `fkit.Section()` object.

* length: float
  * wall length

* width: float
  * wall thickness

* steel_thickness: float
  * thickness of structural steel plate encasing concrete wall

* concrete_fiber: patchfiber object
  * patch fiber object with material properties for concrete
* steel_fiber: patchfiber object
  * patch fiber object with material properties for structural steel plate
* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5
* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# speedcore wall
# also known as concrete-filled composite steel plate shear wall (CF-CPSW)
section8 = fkit.sectionbuilder.wall_speedcore(length=120,
                                              width=18, 
                                              steel_thickness=1,
                                              concrete_fiber=fiber_confined, 
                                              steel_fiber=fiber_structural_steel)
```



### wide_flange()

`fkit.sectionbuilder.wide_flange(bf, d, tw, tf, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)` returns a fully constructed `fkit.Section()` object.

* bf: float
  * flange width

* d: float
  * depth

* tw: float
  * web thickness

* tf: float
  * flange thickness

* steel_fiber: patchfiber object
  * patch fiber object with material properties for structural steel
* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5
* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# structural steel wide-flange section (W) (I beam)
section9 = fkit.sectionbuilder.wide_flange(bf = 14,
                                           d = 14,
                                           tw = 1.0,
                                           tf = 1.5,
                                           steel_fiber = fiber_structural_steel)
```



### W_AISC()

`fkit.sectionbuilder.W_AISC(shape, steel_fiber, mesh_nx=0.5, mesh_ny=0.5)` returns a fully constructed `fkit.Section()` object.

* shape: string
  * valid AISC shape designation (e.g. "W27x307")

* steel_fiber: patchfiber object
  * patch fiber object with material properties for structural steel
* mesh_nx: float (OPTIONAL)
  * mesh density in the x direction (0 being least dense, 1 being most dense)
  * default = 0.5
* mesh_ny: float (OPTIONAL)
  * mesh density in the y direction (0 being least dense, 1 being most dense)
  * default = 0.5



```python
# wide flange section within AISC steel manual (W27X307)
section10 = fkit.sectionbuidler.W_AISC(shape = "W27X307",
                                       steel_fiber = fiber_structural_steel)
```





## APPENDIX: Theoretical Background Moment Curvature

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/fbd.png?raw=true" alt="demo" style="width: 60%;" />
</div>

The figure above depicts state of stress where the external forces (highlighted green), and internal forces (highlighted yellow) are in equilibrium. Note that the strain profile is assumed linear; a fundamental assumption in section analysis known as plane-section-remain-plane.

$$\sum F = 0$$

$$\sum M = 0$$

A moment curvature analysis involves incrementally increasing curvature (shown as $\phi$ in the above diagram, sometimes the Greek letter $\kappa$ is used). At each step, a depth of neutral axis is calculated using a root-finding algorithm in order to satisfy equilibrium. The process is displacement-based and can be thought of as increasingly bending a beam further and further. The figure below illustrates this process.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/momentcurvaturesteps.png?raw=true" alt="demo" style="width: 100%;" />
</div>

The moment curvature analysis algorithm can be summarized as follows:

1. Section is discretized into patch fibers and node fibers
2. Slowly increment curvature from 0 to an user-specified target ($\phi_{target}$)
3. At each curvature ($\phi$), use secant method to search for the depth of neutral axis that satisfies equilibrium. For a given neutral axis depth ($c$) and for each fiber i:
      * Calculate fiber depth with respect to top of section ($d_i$)
      * Calculate fiber strain based on NA depth and curvature ($\epsilon_i = \phi*(d_i - c)$)
      * Calculate fiber stress based on fiber material properties ($\sigma_i =f(\epsilon_i)$)
      * Calculate fiber force contribution ($F_i = \sigma_i A_i$)
        * ($A_i$) is fiber area
      * Calculate fiber moment contribution ($M_i = F_i e_i$)
        * ($e_i$) is the distance between fiber centroid to section centroid
        * ($e_{ix} = x_{fiber} - x_{section}$)
        * ($e_{iy} = y_{fiber} - y_{section}$)
4. Neural axis depth is found if force is in equilibrium (considering applied axial load):
      * $\sum F_i - P = 0 $

5. At the correct NA depth, sum moment about the section centroid
      * $M = \sum M_i $

6. Record this point ($\phi, M$) and move to next curvature increment, loop until reached $\phi_{target}$
                       



## APPENDIX: Theoretical Background P+M Interaction Surface

P+M interaction curves can be derived in two ways:

1. Conduct several moment-curvature analysis at varying level of applied axial load **P** (from max tension to max compression), taking note of peak moment **M**. However, note how we are only interested in a single point out of an entire moment-curvature curve. 
2. Alternatively, we can assume that the ultimate condition occurs where the extreme compression fiber is equal some specific crushing strain (e.g. $\epsilon_{cu} = 0.003$), then increase depth of neutral axis from 0 to infinity. At each neutral axis depth, a new ultimate **(P, M)** point is derived

The second method is computationally more efficient and is summarized graphically in the figure below.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/PMinteractionsteps.png?raw=true" alt="demo" style="width: 100%;" />
</div>
<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/PMinteractionsteps2.png?raw=true" alt="demo" style="width: 70%;" />
</div>

fkit follows the design assumptions outlined in ACI 318-19 to generate its PM interaction curves. In particular:

* concrete fiber material approximated with rectangular stress block
* rebar fiber material approximated with elastic-perfect-plastic
* rectangular stress block parameter: $\alpha = 0.85$
* rectangular stress block parameter: $\beta= f(f'_c)$
* ultimate crushing strain: $\epsilon_{cu} = 0.003$
* concrete fibers does not take tension


The PM interaction analysis algorithm is as follows:

1. Section is discretized into patch fibers and node fibers
2. Slowly increment neutral axis depth (c) from 0 to infinity. 
   * c = 0 represents pure tension; c = inf represents pure compression
3. For a given neutral axis depth ($c$):
   * Calculate curvature ($\phi = \frac{0.003}{c}$)
   * Calculate fiber depth with respect to top of section ($d_i$)
   * Calculate fiber strain based on NA depth and curvature ($\epsilon_i = \phi*(d_i - c)$)
   * Calculate fiber stress based on the following condition:
     * if fiber depth > neutral axis depth: ($\sigma = 0$)
     * if fiber depth < neutral axis depth: ($\sigma = 0.85f'_c$)
   * Calculate fiber force contribution ($F_i = \sigma_i A_i$)
     * ($A_i$) is fiber area
   * Calculate fiber moment contribution ($M_i = F_i e_i$)
     * ($e_i$) is the distance between fiber centroid to section centroid
     * ($e_{ix} = x_{fiber} - x_{section}$)
     * ($e_{iy} = y_{fiber} - y_{section}$)
   * Record ($P,M,c$) and move to next neutral axis depth



