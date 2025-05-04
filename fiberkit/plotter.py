import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os


def preview_fiber(fiber,x_limit=[-0.03, 0.03]):
    """
    Plot the stress-strain relationshiop of a fiber.

    Args:
        fiber           NodeFiber or PatchFiber:: fiber kit patch or node fiber object
        x_limit         (OPTIONAL)[float]:: x-axis limit for plotting. default = [-0.03, 0.03]
    
    Return:
        fig         Figure:: generated matplotlib figure
        
    """
    # plot stress and strain
    strain_x = np.linspace(x_limit[0],x_limit[1],200)
    stress_y = [fiber.stress_strain(a) for a in strain_x]
    
    fig, axs = plt.subplots()
    axs.plot(strain_x,stress_y,c="#435be2")
    
    fig.suptitle("Fiber Stress-Strain Relationship - {}".format(fiber.name))
    axs.set_xlim(x_limit)
    axs.set_xlabel("Strain")
    axs.set_ylabel("Stress")
    axs.xaxis.grid()
    axs.yaxis.grid()
    axs.axhline(y=0, color = "black", linestyle="-", lw = 0.8)
    axs.axvline(x=0, color = "black", linestyle="-", lw = 0.8)
    plt.tight_layout()
    return fig


def compare_fibers(fibers, labels, x_limit):
    """
    Compare material properties of several fibers on a single plot.
    
    Args:
        fibers              [NodeFiber or PatchFiber]:: list of fibers to visualize
        labels              [str]:: list of label to distinguish between fibers.
        x_limit             (OPTIONAL) [float]:: x-axis limit for plotting. default = [-0.03, 0.03]
    
    Return:
        fig             Figure:: generated matplotlib figure
    """
    # range of strain to plot
    fig, axs = plt.subplots()
    strain_x = np.linspace(x_limit[0],x_limit[1],200)

    # loop through all fibers and plot
    for i, f in enumerate(fibers):
        stress_y = [f.stress_strain(a) for a in strain_x]
        axs.plot(strain_x, stress_y, label = labels[i])

    # styling
    fig.suptitle("Fiber Monotonic Stress-Strain Curve")
    axs.set_xlim(x_limit)
    axs.set_xlabel("Strain")
    axs.set_ylabel("Stress")
    axs.xaxis.grid()
    axs.yaxis.grid()
    axs.legend(loc="best")
    axs.axhline(y=0, color = "black", linestyle="-", lw = 0.8)
    axs.axvline(x=0, color = "black", linestyle="-", lw = 0.8)
    
    return fig


def preview_section(section, show_tag=False):
    """
    Preview section geometry
    
    Args:
        section         Section:: fiber kit section object
        show_tag        (OPTIONAL) bool:: flag to show node fiber tags. Default = False

    Return:
        fig             Figure:: generated matplotlib figure
    """
    # mesh just in case it hasn't occured yet
    section.mesh()
    
    # initialize
    fig, axs = plt.subplots(figsize=(11,8.5))
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs.add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.default_color,edgecolor="black",zorder=2,lw=2))
        if show_tag:
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
    """
    Plot moment curvature diagram.
    
    Args:
        section           Section:: fiber kit section object
        
    Return:
        fig         Figure:: generated matplotlib figure
    """
    # exit if no results
    if not section.MK_solved:
        raise RuntimeError("ERROR: Please run moment curvature analysis before plotting")
    
    # init figure
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
    fig.suptitle("Moment Curvature Analysis (P = {:.1f})".format(section.axial), fontweight="bold", fontsize=18)
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
    axs[1].set_xlabel("Curvature", fontsize=12)
    axs[1].set_ylabel("Moment", fontsize=12)
    plt.tight_layout()
    return fig


def plot_MK_3D(section):
    """
    Plot moment curvature results in 3D interactive format using Plotly
    """
    pass


def animate_MK(section):
    """
    Generate a folder of pngs for each load step. The pngs can then be stapled together
    externally into a gif. For example, using ImageMagick: "magick -delay 5 -loop 0 *.png demo.gif"
    
    Args:
        section           Section:: fiber kit section object

    Return:
        None
    """
    # set up animation folder
    if not section.MK_solved:
        raise RuntimeError("ERROR: Please run moment curvature analysis before creating animation")
    if not section.folder_created:
        section.create_output_folder()
    plt.ioff()
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
        fig.suptitle("Fiber kit - Moment Curvature Analysis (P = {:.1f})".format(section.axial), fontweight="bold", fontsize=18)
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
        axs[1].set_xlabel("Curvature", fontsize=12)
        axs[1].set_ylabel("Moment", fontsize=12)
        plt.tight_layout()
        
        filename = os.path.join(save_dir,"frame{:04d}.png".format(i))
        fig.savefig(filename)
        


def plot_PM(section, P=None, M=None):
    """
    Plot ACI 318 PM interaction surface (both nominal and factored).
    
    Args:
        section         Section:: fiber kit section object
        P               (OPTIONAL) (float):: list of axial demands to plot
        M               (OPTIONAL) (float):: list of moment demand to plot
        
    Return: 
        fig         Figure:: generated matplotlib figure
    """
    # exit if no results available
    if not section.PM_solved:
        raise RuntimeError("ERROR: Please run interaction analysis before plotting")
    
    # init figure
    fig, axs = plt.subplots(1,2,figsize=(16,9),gridspec_kw={'width_ratios':[1,1]})
    
    # plot meshes
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs[0].add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.default_color,edgecolor="black",zorder=2))
    for f in section.patch_fibers:
        axs[0].add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.default_color,edgecolor="black",zorder=1,lw=1.0))
    
    # plot centroid
    axs[0].scatter(section.centroid[0], section.centroid[1], c="red", marker="x",linewidth=2,s=300, zorder=3)
    
    # formatting
    fig.suptitle("Section Interaction Diagram (ACI 318)", fontweight="bold", fontsize=18)
    axs[0].xaxis.grid()
    axs[0].yaxis.grid()
    axs[0].set_axisbelow(True)
    axs[0].set_aspect('equal', 'box')

    # plot nominal interaction surface
    # indices: [P,Mx,NA_depth,My,resistance_factor,phi_P,phi_Mx,phi_My]
    M0 = [x for x in section.PM_surface[0][1]]
    P0 = [-x for x in section.PM_surface[0][0]]  # flipped sign so +P is compression
    M180 = [x for x in section.PM_surface[180][1]]
    P180 = [-x for x in section.PM_surface[180][0]] # flipped sign so +P is compression
    axs[1].plot(M0, P0, label="nominal",linestyle="-",c="blue", marker=None)
    axs[1].plot(M180, P180, linestyle="-",c="blue", marker=None)
    
    # find index where factored curve reaches 0.8Po
    Po = min(section.PM_surface[0][5])
    for i in range(len(section.PM_surface[0][5])):
        if section.PM_surface[0][5][i] < 0.8*Po:
            split_index = i
            break
    
    # plot factored curve without the hat
    M0_factored = [x for x in section.PM_surface[0][6][:split_index]]
    P0_factored = [-x for x in section.PM_surface[0][5][:split_index]]
    M180_factored = [x for x in section.PM_surface[180][6][:split_index]]
    P180_factored = [-x for x in section.PM_surface[180][5][:split_index]]
    
    # close off the curve at the top
    M180_factored.append(M0_factored[-1])
    P180_factored.append(P0_factored[-1])
    
    # plot factored interaction surface
    axs[1].plot(M0_factored, P0_factored, label="factored", linestyle="-", c="red")
    axs[1].plot(M180_factored, P180_factored, linestyle="-", c="red")
    
    # plot peak above 0.8Po with dotted line
    M0_factored_top = [x for x in section.PM_surface[0][6][split_index-1:]]
    P0_factored_top = [-x for x in section.PM_surface[0][5][split_index-1:]]
    M180_factored_top = [x for x in section.PM_surface[180][6][split_index-1:]]
    P180_factored_top = [-x for x in section.PM_surface[180][5][split_index-1:]]
    axs[1].plot(M0_factored_top, P0_factored_top, linestyle="--",c="red")
    axs[1].plot(M180_factored_top, P180_factored_top, linestyle="--",c="red")
    
    # styling
    axs[1].xaxis.grid()
    axs[1].yaxis.grid()
    axs[1].axhline(0, color='black')
    axs[1].axvline(0, color='black')
    axs[1].set_xlabel("Moment", fontsize=12)
    axs[1].set_ylabel("Axial Force", fontsize=12)
    axs[1].legend(loc="best")
    plt.tight_layout()
    
    # plot demands
    P = [] if P==None else P
    M = [] if M==None else M
    axs[1].scatter(M, P, c="red", marker="x",linewidth=2,s=100)
    
    return fig




def plot_Icr(section):
    """
    Plot the section's cracked moment of inertia at each load step as a ratio of Ig. 
    
    Args:
        section           Section:: fiber kit section object
    
    Return:
        fig             Figure:: generated matplotlib figure
    """
    # exit if no results
    if not section.Icr_solved:
        raise RuntimeError("ERROR: Please run cracked moment of inertia analysis before plotting")
    
    # set up custom subplots
    fig = plt.figure(figsize=(16,9), dpi=200)
    gs = fig.add_gridspec(2,2)
    axs1 = fig.add_subplot(gs[:, 0])
    axs2 = fig.add_subplot(gs[0, 1])
    axs3 = fig.add_subplot(gs[1, 1], sharex=axs2)
    
    # plot meshes
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs1.add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.color_list[-1],edgecolor="black",zorder=2))
    for f in section.patch_fibers:
        axs1.add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.color_list[-1],edgecolor="black",zorder=1,lw=1.0))
    
    # plot moment curvature
    axs2.plot(section.curvature,section.momentx, lw=3, c="#435be2")
    axs2.plot(section.curvature,section.momenty, linestyle="--")
    
    # plot cracked moment of inertia
    I_ratio = [min(1, I/section.Ig) for I in section.Icr]
    axs3.plot(section.curvature, I_ratio, lw=3, c="#435be2")
    
    # plot centroid
    axs1.scatter(section.xc_cracked[-1], section.yc_cracked[-1], c="red", marker="x",linewidth=2, s=240, zorder=3)
    
    # formatting
    fig.suptitle("Cracked Moment of Inertia Progression (P = {:.1f})".format(section.axial), fontweight="bold", fontsize=18)
    axs1.grid()
    axs1.set_axisbelow(True)
    axs1.set_aspect('equal', 'box')
    
    axs2.grid()
    axs2.axhline(0, color='black')
    axs2.axvline(0, color='black')
    axs2.set_ylabel("Moment", fontsize=12)
    
    axs3.grid()
    axs3.axhline(0, color='black')
    axs3.axvline(0, color='black')
    axs3.set_ylabel("Icr / Ig", fontsize=12)
    axs3.set_xlabel("Curvature", fontsize=12)
    axs3.set_ylim([0,1.1])
    
    plt.tight_layout()
    return fig

    












