# import fkit
import fkit.patchfiber as patches
import fkit.nodefiber as nodes


# available concrete fibers
Hognestad_unconfined  = patches.Hognestad(fpc=6)
Mander_unconfined     = patches.Mander(fpc=5.4)
Todeschini_unconfined = patches.Todeschini(fpc=6)

Hognestad_confined    = patches.Hognestad(fpc=9, eo=0.006, emax=0.023)
Mander_confined       = patches.Mander(fpc=8.1, eo=0.006, emax=0.023)
Todeschini_confined   = patches.Todeschini(fpc=9, eo=0.006, emax=0.023)



# available steel fibers
ElasticPlastic  = nodes.Bilinear(fy=75)
StrainHarden    = nodes.Bilinear(fy=75, beta=0.004)
MultiLinear     = nodes.Multilinear(fy=75, fu=100)
RambergOsgood   = nodes.RambergOsgood(fy=75, n=25)
MenegottoPinto  = nodes.MenegottoPinto(fy=75, n=5)
Trilinear       = nodes.Custom_Trilinear(stress1p=75, strain1p=0.002,
                                         stress2p=100, strain2p=0.1,
                                         stress3p=75, strain3p=0.16,
                                         stress1n=-40, strain1n=-0.001,
                                         stress2n=-5, strain2n=-0.002,
                                         stress3n=-0, strain3n=-0.03)




# range of strain to plot
import matplotlib.pyplot as plt
import numpy as np
fig, axs = plt.subplots()
strain_limit=[-0.06, 0.06]
strain_x = np.linspace(strain_limit[0],strain_limit[1],500)


# select what to plot
# axs.plot(strain_x,[Hognestad_unconfined.stress_strain(a) for a in strain_x],label="Hognestad_unconfined")
# axs.plot(strain_x,[Mander_unconfined.stress_strain(a) for a in strain_x],label="Mander_unconfined")
# axs.plot(strain_x,[Todeschini_unconfined.stress_strain(a) for a in strain_x],label="Todeschini_unconfined")
axs.plot(strain_x,[Hognestad_confined.stress_strain(a) for a in strain_x],label="Hognestad_confined")
axs.plot(strain_x,[Mander_confined.stress_strain(a) for a in strain_x],label="Mander_confined")
axs.plot(strain_x,[Todeschini_confined.stress_strain(a) for a in strain_x],label="Todeschini_confined")

# axs.plot(strain_x,[ElasticPlastic.stress_strain(a) for a in strain_x],label="Elastic-Perfect-Plastic")
# axs.plot(strain_x,[StrainHarden.stress_strain(a) for a in strain_x],label="Bilinear")
# axs.plot(strain_x,[MultiLinear.stress_strain(a) for a in strain_x],label="Multilinear")
# axs.plot(strain_x,[RambergOsgood.stress_strain(a) for a in strain_x],label="RambergOsgood")
# axs.plot(strain_x,[MenegottoPinto.stress_strain(a) for a in strain_x],label="MenegottoPinto")
# axs.plot(strain_x,[Trilinear.stress_strain(a) for a in strain_x],label="BarBuckling")


# styling
fig.suptitle("Fiber Monotonic Stress-Strain Curve")
axs.set_xlim(strain_limit)
axs.set_xlabel("strain")
axs.set_ylabel("stress")
axs.xaxis.grid()
axs.yaxis.grid()
axs.legend(loc="best")
axs.axhline(y=0, color = "black", linestyle="-", lw = 0.8)
axs.axvline(x=0, color = "black", linestyle="-", lw = 0.8)

