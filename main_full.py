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


