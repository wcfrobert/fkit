import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os


def preview_fiber(fiber,x_limit=[-0.03, 0.03]):
    """plot monotonic stress-strain curve of a defined fiber"""
    strain_x = np.linspace(x_limit[0],x_limit[1],500)
    stress_y = [fiber.stress_strain(a) for a in strain_x]
    
    fig, axs = plt.subplots()
    axs.plot(strain_x,stress_y,c="#435be2")
    
    fig.suptitle("Fiber Stress-Strain - {}".format(fiber.name))
    axs.set_xlim(x_limit)
    axs.set_xlabel("strain")
    axs.set_ylabel("stress")
    axs.xaxis.grid()
    axs.yaxis.grid()
    axs.axhline(y=0, color = "black", linestyle="-", lw = 0.8)
    axs.axvline(x=0, color = "black", linestyle="-", lw = 0.8)
    plt.tight_layout()
    return fig, strain_x, stress_y


def preview_section(section, show_bartag=False):
    """preview section geometry"""
    # initialize
    fig, axs = plt.subplots(figsize=(11,8.5))
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs.add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.default_color,edgecolor="black",zorder=2,lw=2))
        if show_bartag:
            axs.annotate("{}".format(f.tag), xy=(f.coord[0],f.coord[1]), xycoords='data', xytext=(0, 15), textcoords='offset points', fontsize=24, c="red")
    for f in section.patch_fibers:
        axs.add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.default_color,edgecolor="black",zorder=1,lw=1.0))
        
    # plot centroid
    axs.scatter(section.centroid[0], section.centroid[1], c="red", marker="x",linewidth=3, s=240, zorder=3)

    # formatting
    fig.suptitle("Section Mesh")
    axs.xaxis.grid()
    axs.yaxis.grid()
    axs.set_axisbelow(True)
    axs.set_aspect('equal', 'box')
    plt.tight_layout()
    return fig


def plot_MK(section):
    if not section.MK_solved:
        raise RuntimeError("Please run moment curvature analysis before plotting")
        
    fig, axs = plt.subplots(1,2,figsize=(16,9),gridspec_kw={'width_ratios':[1,1]})
    
    # plot meshes
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs[0].add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.color_list[-1],edgecolor="black",zorder=2))
    for f in section.patch_fibers:
        axs[0].add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.color_list[-1],edgecolor="black",zorder=1,lw=1.0))
    
    # plot centroid
    axs[0].scatter(section.centroid[0], section.centroid[1], c="red", marker="x",linewidth=3,s=240, zorder=3)
    
    # formatting
    fig.suptitle("Moment Curvature Analysis (P = {})".format(section.axial))
    axs[0].xaxis.grid()
    axs[0].yaxis.grid()
    axs[0].set_axisbelow(True)
    axs[0].set_aspect('equal', 'box')

    # plot Moment Curvature
    axs[1].plot(section.curvature,section.momentx, lw=3, c="#435be2")
    axs[1].plot(section.curvature,section.momenty, linestyle="--")
    #axs[1].legend(loc="best")
    axs[1].xaxis.grid()
    axs[1].yaxis.grid()
    axs[1].axhline(0, color='black')
    axs[1].axvline(0, color='black')
    axs[1].set_xlabel("Curvature")
    axs[1].set_ylabel("Moment")
    plt.tight_layout()
    return fig


def animate_MK(section):
    """generate a folder containing pngs which can be converted to gif"""
    plt.ioff()
    if not section.MK_solved:
        raise RuntimeError("Please run moment curvature analysis before animating")
        
    if not section.folder_created:
        section.create_output_folder()
    
    N_frame = len(section.curvature)
    save_dir = os.path.join(section.output_dir, "animate")
    os.makedirs(save_dir)
    
    for i in range(N_frame):  
        print("\tcreating frame {}...".format(i))
        fig, axs = plt.subplots(1,2,figsize=(16,9),gridspec_kw={'width_ratios':[1,1]})
        
        # plot meshes
        for f in section.node_fibers:
            radius = (f.area/3.1415926)**(0.5)
            axs[0].add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.color_list[i],edgecolor="black",zorder=2))
        for f in section.patch_fibers:
            axs[0].add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.color_list[i],edgecolor="black",zorder=1,lw=1.0))
        
        # plot centroid
        axs[0].scatter(section.centroid[0], section.centroid[1], c="red", marker="x",linewidth=3,s=240, zorder=3)
        
        # formatting
        fig.suptitle("Moment Curvature Analysis (P = {})".format(section.axial))
        axs[0].xaxis.grid()
        axs[0].yaxis.grid()
        axs[0].set_axisbelow(True)
        axs[0].set_aspect('equal', 'box')
    
        # plot Moment Curvature
        axs[1].plot(section.curvature[:i],section.momentx[:i], lw=3, c="#435be2")
        axs[1].set_xlim(0, max(section.curvature)*1.1)
        axs[1].set_ylim(0, max(section.momentx)*1.1)
        axs[1].xaxis.grid()
        axs[1].yaxis.grid()
        axs[1].axhline(0, color='black')
        axs[1].axvline(0, color='black')
        axs[1].set_xlabel("Curvature")
        axs[1].set_ylabel("Moment")
        plt.tight_layout()
        
        filename = os.path.join(save_dir,"frame{:04d}.png".format(i))
        fig.savefig(filename)
        #magick -delay 5 -loop 0 *.png demo.gif


def plot_PM_ACI(section, P=[], M=[]):
    """
    Plot section ACI 318 PM interaction surface (both nominal and factored)
    Please Note:
        Internally within fkit, the sign convention is +P = tension, -P = compression
        This is opposite of what's commonly used within the concrete design industry.
        For plotting and exporting purposes, the sign on P is flipped.
    """
    if not section.PM_solved_ACI:
        raise RuntimeError("Please run ACI interaction analysis before plotting")
        
    fig, axs = plt.subplots(1,2,figsize=(16,9),gridspec_kw={'width_ratios':[1,1]})
    
    # plot meshes
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs[0].add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.default_color,edgecolor="black",zorder=2))
    for f in section.patch_fibers:
        axs[0].add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.default_color,edgecolor="black",zorder=1,lw=1.0))
    
    # plot centroid
    axs[0].scatter(section.centroid[0], section.centroid[1], c="red", marker="x",linewidth=3,s=300, zorder=3)
    
    # formatting
    fig.suptitle("Section Interaction Surface (ACI-318)")
    axs[0].xaxis.grid()
    axs[0].yaxis.grid()
    axs[0].set_axisbelow(True)
    axs[0].set_aspect('equal', 'box')

    # plot interaction surface
    # flipping P sign convention to match concrete design industry standard
    # where +P is compression, -P is tension
    original_Mf = [m for m in section.PM_surface_ACI_factored[0][1]]
    original_Pf = [-m for m in section.PM_surface_ACI_factored[0][0]]
    flipped_Mf = [m for m in section.PM_surface_ACI_factored[180][1]]
    flipped_Pf = [-m for m in section.PM_surface_ACI_factored[180][0]]

    original_M = [m for m in section.PM_surface_ACI[0][1]]
    original_P = [-m for m in section.PM_surface_ACI[0][0]]
    flipped_M = [m for m in section.PM_surface_ACI[180][1]]
    flipped_P = [-m for m in section.PM_surface_ACI[180][0]]

    axs[1].plot(original_M, original_P, label="nominal",linestyle="--",c="red")
    axs[1].plot(flipped_M, flipped_P, label="nominal",linestyle="--",c="red")
    
    axs[1].plot(original_Mf, original_Pf, label="factored",c="blue")
    axs[1].plot(flipped_Mf, flipped_Pf, label="factored",c="blue")
    
    axs[1].xaxis.grid()
    axs[1].yaxis.grid()
    axs[1].axhline(0, color='black')
    axs[1].axvline(0, color='black')
    axs[1].set_xlabel("Moment")
    axs[1].set_ylabel("Axial Force")
    plt.tight_layout()
    
    # plot demands
    axs[1].scatter(M, P, c="red", marker="x",linewidth=2,s=100)
    
    return fig








def plot_PM(section, P=[], M=[]):
    """
    Plot section PM interaction surface based on user defined fibers
    Please Note:
        Internally within fkit, the sign convention is +P = tension, -P = compression
        This is opposite of what's commonly used within the concrete design industry.
        For plotting and exporting purposes, the sign on P is flipped.
    """
    if not section.PM_solved:
        raise RuntimeError("Please run interaction analysis before plotting")
        
    fig, axs = plt.subplots(1,2,figsize=(16,9),gridspec_kw={'width_ratios':[1,1]})
    
    # plot meshes
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs[0].add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.default_color,edgecolor="black",zorder=2))
    for f in section.patch_fibers:
        axs[0].add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.default_color,edgecolor="black",zorder=1,lw=1.0))
    
    # plot centroid
    axs[0].scatter(section.centroid[0], section.centroid[1], c="red", marker="x",linewidth=3,s=300, zorder=3)
    
    # formatting
    fig.suptitle("Section Interaction Surface")
    axs[0].xaxis.grid()
    axs[0].yaxis.grid()
    axs[0].set_axisbelow(True)
    axs[0].set_aspect('equal', 'box')

    # plot interaction surface
    # flipping P sign convention to match concrete design industry standard
    # where +P is compression, -P is tension
    original_M = [m for m in section.PM_surface[0][1]]
    original_P = [-m for m in section.PM_surface[0][0]]
    flipped_M = [m for m in section.PM_surface[180][1]]
    flipped_P = [-m for m in section.PM_surface[180][0]]

    axs[1].plot(original_M, original_P, label="nominal",linestyle="--",c="red")
    axs[1].plot(flipped_M, flipped_P, label="nominal",linestyle="--",c="red")
    
    axs[1].xaxis.grid()
    axs[1].yaxis.grid()
    axs[1].axhline(0, color='black')
    axs[1].axvline(0, color='black')
    axs[1].set_xlabel("Moment")
    axs[1].set_ylabel("Axial Force")
    plt.tight_layout()
    
    # plot demands
    axs[1].scatter(M, P, c="red", marker="x",linewidth=2,s=100)
    
    return fig

