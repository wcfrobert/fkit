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


