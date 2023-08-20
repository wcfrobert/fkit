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



