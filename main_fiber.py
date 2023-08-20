# import fkit
from fkit.plotter import compare_fibers
import fkit.patchfiber as patches
import fkit.nodefiber as nodes



# concrete fibers
Hognestad_unconfined  = patches.Hognestad(fpc=4)
Todeschini_unconfined = patches.Todeschini(fpc=4)
Hognestad_confined    = patches.Hognestad(fpc=6.7, eo=0.006, emax=0.023)
Mander_confined       = patches.Mander(fpc=6, eo=0.006, emax=0.023)

compare_fibers(fibers = [Hognestad_unconfined,Todeschini_unconfined], 
               labels = ["Hognestad_unconfined","Todeschini_unconfined"],
               x_limit = [-0.005, 0.005])

compare_fibers(fibers = [Hognestad_confined,Mander_confined], 
               labels = ["Hognestad_confined","Mander_confined"],
               x_limit = [-0.03, 0.03])

compare_fibers(fibers = [Hognestad_confined,Hognestad_unconfined], 
               labels = ["Hognestad_confined","Hognestad_unconfined"],
               x_limit = [-0.03, 0.03])




# steel fibers
ElasticPlastic  = nodes.Bilinear(fy=60, Es=29000, emax=0.16)
StrainHarden    = nodes.Bilinear(fy=60, fu=90, Es=29000, emax=0.16)
MultiLinear     = nodes.Multilinear(fy=60, fu=90, Es=29000)
RambergOsgood   = nodes.RambergOsgood(fy=60, n=25, Es=29000)
MenegottoPinto  = nodes.MenegottoPinto(fy=60, n=5, b=0.0043, Es=29000)
Trilinear       = nodes.Custom_Trilinear(stress1p=60, strain1p=0.002,
                                         stress2p=90, strain2p=0.1,
                                         stress3p=75, strain3p=0.16,
                                         stress1n=-40, strain1n=-0.001,
                                         stress2n=-5, strain2n=-0.002,
                                         stress3n=-0, strain3n=-0.03)


compare_fibers(fibers = [ElasticPlastic, StrainHarden, MultiLinear], 
               labels = ["Elastic-Perfect-Plastic","Strain Hardening", "Multilinear"],
               x_limit = [-0.05, 0.05])

compare_fibers(fibers = [ElasticPlastic, StrainHarden, MultiLinear], 
               labels = ["Elastic-Perfect-Plastic","Strain Hardening", "Multilinear"],
               x_limit = [-0.17, 0.17])

compare_fibers(fibers = [RambergOsgood , MenegottoPinto , StrainHarden], 
               labels = ["RambergOsgood" , "MenegottoPinto" , "Bilinear"],
               x_limit = [-0.05, 0.05])

compare_fibers(fibers = [RambergOsgood , MenegottoPinto , StrainHarden], 
               labels = ["RambergOsgood" , "MenegottoPinto" , "Bilinear"],
               x_limit = [-0.17, 0.17])



