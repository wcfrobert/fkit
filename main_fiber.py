import fiberkit as fkit

# concrete patch fibers
Hognestad_unconfined  = fkit.patchfiber.Hognestad(fpc=4)
Todeschini_unconfined = fkit.patchfiber.Todeschini(fpc=4)
Hognestad_confined    = fkit.patchfiber.Hognestad(fpc=6.7, eo=0.006, emax=0.023)
Mander_confined       = fkit.patchfiber.Mander(fpc=6, eo=0.006, emax=0.023)

fkit.plotter.compare_fibers(fibers = [Hognestad_unconfined,Todeschini_unconfined], 
                            labels = ["Hognestad_unconfined","Todeschini_unconfined"],
                            x_limit = [-0.005, 0.005])

fkit.plotter.compare_fibers(fibers = [Hognestad_confined,Mander_confined], 
                            labels = ["Hognestad_confined","Mander_confined"],
                            x_limit = [-0.03, 0.03])

fkit.plotter.compare_fibers(fibers = [Hognestad_confined,Hognestad_unconfined], 
                            labels = ["Hognestad_confined","Hognestad_unconfined"],
                            x_limit = [-0.03, 0.03])


# steel node fibers
ElasticPlastic  = fkit.nodefiber.Bilinear(fy=60, Es=29000, emax=0.16)
StrainHarden    = fkit.nodefiber.Bilinear(fy=60, fu=90, Es=29000, emax=0.16)
MultiLinear     = fkit.nodefiber.Multilinear(fy=60, fu=90, Es=29000)
RambergOsgood   = fkit.nodefiber.RambergOsgood(fy=60, n=25, Es=29000)
MenegottoPinto  = fkit.nodefiber.MenegottoPinto(fy=60, n=5, b=0.0043, Es=29000)
Trilinear       = fkit.nodefiber.Custom_Trilinear(stress1p=60, strain1p=0.002,
                                                  stress2p=90, strain2p=0.1,
                                                  stress3p=75, strain3p=0.16,
                                                  stress1n=-40, strain1n=-0.001,
                                                  stress2n=-5, strain2n=-0.002,
                                                  stress3n=-0, strain3n=-0.03)

fkit.plotter.compare_fibers(fibers = [ElasticPlastic, StrainHarden, MultiLinear], 
                            labels = ["Elastic-Perfect-Plastic","Strain Hardening", "Multilinear"],
                            x_limit = [-0.05, 0.05])

fkit.plotter.compare_fibers(fibers = [ElasticPlastic, StrainHarden, MultiLinear], 
                            labels = ["Elastic-Perfect-Plastic","Strain Hardening", "Multilinear"],
                            x_limit = [-0.17, 0.17])

fkit.plotter.compare_fibers(fibers = [RambergOsgood , MenegottoPinto , StrainHarden], 
                            labels = ["RambergOsgood" , "MenegottoPinto" , "Bilinear"],
                            x_limit = [-0.05, 0.05])

fkit.plotter.compare_fibers(fibers = [RambergOsgood , MenegottoPinto , StrainHarden], 
                            labels = ["RambergOsgood" , "MenegottoPinto" , "Bilinear"],
                            x_limit = [-0.17, 0.17])



