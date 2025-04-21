import fkit

"""
#########################################
Step 1: Define fiber material properties
#########################################
"""
# define fiber material properties
fiber_unconfined = fkit.patchfiber.Hognestad(fpc=5)
fiber_confined   = fkit.patchfiber.Mander(fpc=6, eo=0.004, emax=0.014, default_color="gray")
fiber_steel      = fkit.nodefiber.Bilinear(fy=60, fu=90, Es=30000)

# preview fibers
fkit.plotter.preview_fiber(fiber_unconfined, x_limit=[-0.008, 0.008], display_unit="us")
fkit.plotter.preview_fiber(fiber_confined, x_limit=[-0.03, 0.03], display_unit="us")
fkit.plotter.preview_fiber(fiber_steel, x_limit=[-0.03, 0.03], display_unit="us")



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
# let's define this section: https://opensees.berkeley.edu/wiki/index.php/Moment_Curvature_Example
section2 = fkit.sectionbuilder.rectangular_confined(width = 15, 
                                                    height = 24, 
                                                    cover = 1.5, 
                                                    top_bar = [0.6, 3, 1, 0], #[bar_area, nx, ny, y_spacing]
                                                    bot_bar = [0.6, 3, 1, 0], #[bar_area, nx, ny, y_spacing]
                                                    core_fiber = fiber_confined, 
                                                    cover_fiber = fiber_unconfined, 
                                                    steel_fiber = fiber_steel,
                                                    mesh_nx=0.75,
                                                    mesh_ny=0.75)
section2.add_bar(coord = [6, 0], area = 0.6, fiber = fiber_steel)
section2.add_bar(coord = [-6, 0], area = 0.6, fiber = fiber_steel)
section2.mesh()

# preview section
fkit.plotter.preview_section(section1)
fkit.plotter.preview_section(section2, show_tag=True)


"""
#########################################
Step 3: Moment curvature analysis
#########################################
"""
# roughly estimate target curvature, which is a measure of how much to push the section.
phi_target = 0.00125

# moment-curvature analysis
MK_results = section2.run_moment_curvature(phi_target = phi_target, P=-180)

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
fkit.plotter.plot_MK(section2, display_unit="us")
fkit.plotter.plot_Icr(section2, display_unit="us")

# animate results
# fkit.plotter.animate_MK(section2, display_unit="us")


"""
#########################################
Step 4: PMM interaction analysis
#########################################
"""
# generate PM interaction surface using ACI-318 provisions
PM_results = section2.run_PM_interaction(fpc=6, fy=60, Es=29000)

# plot PM interaction surface
fkit.plotter.plot_PM(section2, P=[50,400], M=[-500,3000], display_unit="us")