# import fkit
import fkit
from fkit.plotter import plot_MK, plot_PM_ACI
from fkit.patchfiber import Hognestad
from fkit.nodefiber import Bilinear

# define fibers
fiber_concrete = Hognestad(fpc=5, take_tension=True)
fiber_steel    = Bilinear(fy=60)

# Most common sections can be defined with SectionBuilder
section1 = fkit.sectionbuilder.rectangular(width = 24, height = 24, cover = 1.5,
                                           top_bar = [0.6, 2, 1, 0],
                                           bot_bar = [0.6, 4, 2, 3],
                                           concrete_fiber = fiber_concrete,
                                           steel_fiber = fiber_steel,
                                           mesh_nx=1,
                                           mesh_ny=1)

# moment curvature
section1.run_moment_curvature(phi_max=0.0005, N_step=150)

# P+M interaction
section1.run_interaction_ACI(fpc=5, fy=60)

# plot results
plot_MK(section1)
plot_PM_ACI(section1)

# export results to csv
section1.export_data()






