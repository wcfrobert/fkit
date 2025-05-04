import fiberkit as fkit


# define some fibers we will use later
fiber_unconfined       = fkit.patchfiber.Todeschini(fpc=5, eo=0.002, emax=0.006, default_color="lightgray")
fiber_confined         = fkit.patchfiber.Mander(fpc=6, eo=0.004, emax=0.014, default_color="gray")
fiber_structural_steel = fkit.patchfiber.Multilinear(fy=50, fu=80, Es=29000, default_color="steelblue")
fiber_rebar            = fkit.nodefiber.Bilinear(fy=60, fu=75, Es=29000, emax=0.16, default_color="black")

# rectangular
section1 = fkit.sectionbuilder.rectangular(
    width = 36,
    height = 12,
    cover = 1.5,
    top_bar = [0.3, 6, 1, 0],
    bot_bar = [0.3, 6, 1, 0],
    concrete_fiber = fiber_unconfined,
    steel_fiber = fiber_rebar)
fkit.plotter.preview_section(section1)

# rectangular_confined
section2 = fkit.sectionbuilder.rectangular_confined(
    width = 15, 
    height = 24, 
    cover = 1.5, 
    top_bar = [0.6, 3, 1, 0], 
    bot_bar = [0.6, 3, 2, 3], 
    core_fiber = fiber_confined, 
    cover_fiber = fiber_unconfined, 
    steel_fiber = fiber_rebar)
fkit.plotter.preview_section(section2)

# circular
section3 = fkit.sectionbuilder.circular(
    diameter = 36,
    cover = 2,
    N_bar = 6,
    A_bar = 1.0,
    core_fiber = fiber_confined, 
    cover_fiber = fiber_unconfined, 
    steel_fiber = fiber_rebar)
fkit.plotter.preview_section(section3)

# flanged
section4 = fkit.sectionbuilder.flanged(
    bw = 24,
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
fkit.plotter.preview_section(section4)

# wall
section5 = fkit.sectionbuilder.wall(
    width=12,
    length=120, 
    cover=1.5, 
    wall_bar=[0.31, 12, 2],
    concrete_fiber = fiber_unconfined,
    steel_fiber = fiber_rebar)
fkit.plotter.preview_section(section5)

# wall_BE
section6 = fkit.sectionbuilder.wall_BE(
    width = 18, 
    length = 160, 
    cover = 2, 
    BE_length = 24, 
    wall_bar = [0.31, 6, 2], 
    BE_bar = [1.0, 3, 4],
    concrete_fiber = fiber_unconfined, 
    BE_fiber = fiber_confined, 
    steel_fiber = fiber_rebar)
fkit.plotter.preview_section(section6)

# wall_layered
section7 = fkit.sectionbuilder.wall_layered(
    width1 = 6, 
    width2 = 12, 
    length = 120, 
    cover = 1.5, 
    wall_bar1 = [0.2, 12, 2], 
    wall_bar2 = [0.6, 6, 2],
    concrete_fiber1 = fiber_unconfined, 
    concrete_fiber2 = fiber_confined, 
    steel_fiber1 = fiber_rebar, 
    steel_fiber2 = fiber_rebar)
fkit.plotter.preview_section(section7)

# wall_speedcore
section8 = fkit.sectionbuilder.wall_speedcore(
    length=120,
    width=18, 
    steel_thickness=1,
    concrete_fiber=fiber_confined, 
    steel_fiber=fiber_structural_steel)
fkit.plotter.preview_section(section8)

# wide_flange
section9 = fkit.sectionbuilder.wide_flange(
    bf = 14,
    d = 14,
    tw = 1.0,
    tf = 1.5,
    steel_fiber = fiber_structural_steel)
fkit.plotter.preview_section(section9)

# W_AISC
section10 = fkit.sectionbuilder.W_AISC(
    shape = "W27X307",
    steel_fiber = fiber_structural_steel)
fkit.plotter.preview_section(section10)
