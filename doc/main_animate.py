# import fkit
import fkit
from fkit.patchfiber import Todeschini
from fkit.patchfiber import Mander
from fkit.nodefiber import Bilinear


# define fiber material properties
fiber_unconfined = Todeschini(fpc=5, eo=0.002, emax=0.006, default_color="lightgray", take_tension=True)
fiber_confined   = Mander(fpc=6, eo=0.004, emax=0.014, default_color="gray", take_tension=True)
fiber_steel      = Bilinear(fy=60, beta=0.01, emax=0.16, default_color="black")

# alternatively, most common sections can be quickly defined with SectionBuilder
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

# rotate and mesh section
section2.add_bar(coord=[-6,0], area=0.6, fiber=fiber_steel)
section2.add_bar(coord=[6,0], area=0.6, fiber=fiber_steel)
section2.mesh()


# moment-curvature analysis
section2.run_moment_curvature(P=-180, phi_max=0.0039, N_step=100)

# plot results
fkit.plotter.plot_MK(section2)


# animate results
fkit.plotter.animate_MK(section2)


