import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MaxNLocator
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']) 

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "browser"

import numpy as np
import os
import math


def preview_fiber(fiber,x_limit=[-0.01, 0.01]):
    """
    Plot the stress-strain relationshiop of a fiber.

    Args:
        fiber           NodeFiber or PatchFiber:: fiber kit patch or node fiber object
        x_limit         (OPTIONAL)[float]:: x-axis limit for plotting. default = [-0.01, 0.01]
    
    Return:
        fig         Figure:: generated matplotlib figure
        
    """
    # plot stress and strain
    strain_x = np.linspace(x_limit[0],x_limit[1],200)
    stress_y = [fiber.stress_strain(a) for a in strain_x]
    
    fig, axs = plt.subplots(figsize=(10,6))
    axs.plot(strain_x,stress_y, c="#435be2", lw=2)
    
    fig.suptitle("Fiber Stress-Strain Relationship - {}".format(fiber.name), fontweight="bold", fontsize=12)
    axs.set_xlim(x_limit)
    axs.set_xlabel("Strain")
    axs.set_ylabel("Stress")
    axs.xaxis.grid(linewidth=0.5, color="lightgray")
    axs.yaxis.grid(linewidth=0.5, color="lightgray")
    axs.axhline(y=0, color = "black", linestyle="-", lw = 0.8)
    axs.axvline(x=0, color = "black", linestyle="-", lw = 0.8)
    plt.tight_layout()
    return fig


def compare_fibers(fibers, labels, x_limit=[-0.01, 0.01]):
    """
    Compare material properties of several fibers on a single plot.
    
    Args:
        fibers              [NodeFiber or PatchFiber]:: list of fibers to visualize
        labels              [str]:: list of label to distinguish between fibers.
        x_limit             (OPTIONAL) [float]:: x-axis limit for plotting. default = [-0.01, 0.01]
    
    Return:
        fig             Figure:: generated matplotlib figure
    """
    # range of strain to plot
    fig, axs = plt.subplots(figsize=(10,6))
    strain_x = np.linspace(x_limit[0],x_limit[1],200)
    
    
    # loop through all fibers and plot
    for i, f in enumerate(fibers):
        stress_y = [f.stress_strain(a) for a in strain_x]
        axs.plot(strain_x, stress_y, label = labels[i], lw=2)

    # styling
    fig.suptitle("Fiber Stress-Strain Relationship", fontweight="bold", fontsize=14)
    axs.set_xlim(x_limit)
    axs.set_xlabel("Strain")
    axs.set_ylabel("Stress")
    axs.xaxis.grid(linewidth=0.5, color="lightgray")
    axs.yaxis.grid(linewidth=0.5, color="lightgray")
    axs.legend(loc="best")
    axs.axhline(y=0, color = "black", linestyle="-", lw = 0.8)
    axs.axvline(x=0, color = "black", linestyle="-", lw = 0.8)
    plt.tight_layout()
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
    fig, axs = plt.subplots(figsize=(10,6))
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs.add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.default_color,edgecolor="black",zorder=2,lw=2))
        if show_tag:
            axs.annotate("{}".format(f.tag), xy=(f.coord[0],f.coord[1]), xycoords='data', xytext=(0, 15), textcoords='offset points', fontsize=12, c="red")
    for f in section.patch_fibers:
        axs.add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.default_color,edgecolor="black",zorder=1,lw=0.5))
        
    # plot centroid
    axs.scatter(section.centroid[0], section.centroid[1], c="red", marker="x", linewidth=1, s=100, zorder=3)

    # formatting
    fig.suptitle("Section Preview", fontweight="bold", fontsize=10)
    axs.grid(False)
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
        axs[0].add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.color_list[-1],edgecolor="black",zorder=1,lw=0.65))
    
    # for plot with only patches, we need to insert an invisible node otherwise axes limit are messed up
    axs[0].plot([0],[0], markersize=0)
    
    # check if orthogonal axis moment is significant (>5% of major axis)
    if abs(section.momenty[-1]) > 0.05*abs(section.momentx[-1]):
        plot_minor_axis_moment_too = True
    else:
        plot_minor_axis_moment_too = False
    
    # plot Moment Curvature
    axs[1].xaxis.set_major_locator(MaxNLocator(nbins=8))
    axs[1].yaxis.set_major_locator(MaxNLocator(nbins=12))
    if plot_minor_axis_moment_too:
        axs[1].plot(section.curvature, section.momentx, lw=1.75, c="#435be2", label="MomentX")
        axs[1].plot(section.curvature, section.momenty, lw=1.75, c="#435be2", linestyle="--", label="MomentY")
        axs[1].legend(loc="best")
    else:
        axs[1].plot(section.curvature, section.momentx, lw=1.75, c="#435be2", label="MomentX")
        axs[1].set_ylim([0, 1.1*max(section.momentx)])


    # styling
    if math.isclose(section.axial,0):
        fig.suptitle("Moment Curvature Analysis", fontweight="bold", fontsize=18)
    else:
        fig.suptitle("Moment Curvature Analysis (P = {:.1f})".format(section.axial), fontweight="bold", fontsize=18)
    axs[0].grid(False)
    axs[0].set_aspect('equal', 'box')
    axs[1].set_xlim([0, 1.1*max(section.curvature)])
    axs[1].grid(linewidth=0.75, color="lightgray")
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
    # exit if no results
    if not section.MK_solved:
        raise RuntimeError("ERROR: Please run moment curvature analysis before plotting")
        
    # extract MK results
    mk_results = section.df_MK_results
    
    # extract all fiber data first
    df_nodefibers, df_patchfibers = section.get_all_fiber_data()
    node_fiber_exists = True if df_nodefibers is not None else False # wow python is literally english
    patch_fiber_exists = True if df_patchfibers is not None else False
        
    # initialize plotly subplots
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Section Stress Profile", "Moment Curvature"),
                        column_widths=[0.5, 0.5],
                        horizontal_spacing=0.02,
                        specs = [[{"type":"scene"}, {"type":"xy"}]])
    hovertemplate = '%{text}<extra></extra>'

    # generate frames
    frames = []
    STEP = 0
    N_FRAME=len(section.curvature)
    N_STATIC_TRACES = 0
    print("Generating visualization at each load step...")
    for i in range(N_FRAME):
        print(f"\t step {STEP+1}")
        data = []
        #############################################
        #  STATIC MOMENT CURVATURE LINE
        #############################################
        mk_trace = go.Scatter(x = mk_results["Curvature"],
                                y = mk_results["Moment"],
                                mode="lines",
                                line_width = 2,
                                line_color = "mediumblue",
                                showlegend=False,
                                hovertemplate='Moment = %{y}<br>Curvature = %{x:.2e}<extra></extra>')
        if STEP == 0:
            fig.add_trace(mk_trace, row=1, col=2)
            N_STATIC_TRACES +=1
        
        
        #############################################
        #  STATIC PATCH FIBER MESH
        #############################################
        if patch_fiber_exists:
            # loop through all patch fibers and construct mesh connectivity
            x_list, y_list, z_list = [], [], []
            i_list, j_list, k_list = [], [], []
            facecolor_list = []
            for i in range(len(df_patchfibers)):
                vertices = df_patchfibers.loc[i, "vertices"]
                for j in range(4):
                    x_list.append(vertices[j][0])
                    y_list.append(0)
                    z_list.append(vertices[j][1]) # swapped y <> z for plotting
                
                # first triangle (bottom right)
                i_list.append(i*4)
                j_list.append(i*4 + 1)
                k_list.append(i*4 + 2)
                
                # second triangle (top left)
                i_list.append(i*4 + 2)
                j_list.append(i*4 + 3)
                k_list.append(i*4)
                
                # face color
                color = df_patchfibers.loc[i, "default_color"]
                facecolor_list.append(color)
                facecolor_list.append(color)
                
            # plot patch fibers
            patch_trace = go.Mesh3d(x = x_list, 
                                    y = y_list,
                                    z = z_list,
                                    i = i_list,
                                    j = j_list,
                                    k = k_list,
                                    hoverinfo="skip",
                                    facecolor=facecolor_list,
                                    showlegend=False)
            if STEP == 0:
                fig.add_trace(patch_trace, row=1, col=1)
                N_STATIC_TRACES +=1
        
        

        #############################################
        #  STATIC NODE FIBER MESH
        #############################################
        if node_fiber_exists:
            # loop through all node fibers
            x_list, y_list, z_list = [], [], []
            i_list, j_list, k_list = [], [], []
            facecolor_list = []
            thetas = np.linspace(0, 2*np.pi, 9)
            for i in range(len(df_nodefibers)):
                xc = df_nodefibers.loc[i, "x"]
                zc = df_nodefibers.loc[i, "y"] # swapped y <> z for plotting
                area = df_nodefibers.loc[i, "area"]
                radius = (area/np.pi)**(1/2)
                
                # each node fiber is converted into 10 points around a circle. 0 at center, 1-9 along perimeter. Last pt repeated.
                x_list.append(xc)
                y_list.append(0.1)
                z_list.append(zc)
                for j in range(len(thetas)):
                    x_list.append(xc + radius*np.cos(thetas[j]))
                    y_list.append(0.1)
                    z_list.append(zc + radius*np.sin(thetas[j]))
                    
                # do this twice because i want to plot node fiber on both sides of section
                x_list.append(xc)
                y_list.append(-0.1)
                z_list.append(zc)
                for j in range(len(thetas)):
                    x_list.append(xc + radius*np.cos(thetas[j]))
                    y_list.append(-0.1)
                    z_list.append(zc + radius*np.sin(thetas[j]))
                
                # approximate circle as a polygon with 8 triangles
                for j in range(8):
                    i_list.append(  (20*i)+(j+1)  )
                    j_list.append(  (20*i)+(j+2)  )
                    k_list.append(  (20*i)  )
                
                # again repeat for both sides
                for j in range(8):
                    i_list.append(  (20*i) +10+j+1  )
                    j_list.append(  (20*i) +10+j+2  )
                    k_list.append(  (20*i) +10 )
                
                # face color
                color = df_nodefibers.loc[i, "default_color"]
                for j in range(16):
                    facecolor_list.append(color)
                
            # plot nodes
            node_trace = go.Mesh3d(x = x_list, 
                                   y = y_list,
                                   z = z_list,
                                   i = i_list,
                                   j = j_list,
                                   k = k_list,
                                   hoverinfo="skip",
                                   facecolor=facecolor_list,
                                   showlegend=False)
            if STEP == 0:
                fig.add_trace(node_trace, row=1, col=1)
                N_STATIC_TRACES +=1
        
        
        #############################################
        #  STATIC INVISIBLE NODES AT SCENE EXTENT
        #############################################
        invisible_nodes = go.Scatter3d(x = [0,0], 
                                        y = [-16, 16],
                                        z = [0,0],
                                        mode="markers",
                                        marker_size=6,
                                        marker_color="rgba(255, 255, 255, 0)",
                                        showlegend=False,
                                        hoverinfo="skip",
                                        )
        if STEP == 0:
            fig.add_trace(invisible_nodes, row=1, col=1)
            N_STATIC_TRACES +=1
        
        
        
        #############################################
        #  DYNAMIC STRESS ARROW PLOTS
        #############################################
        # PATCHES
        if patch_fiber_exists:
            # scaling size of vector
            u_max = 8 # max arrow length is 8 units long
            stress_max = 0 # find absmax stress of all fibers in all time steps
            for i in range(len(df_patchfibers)):
                max_stress_for_one_fiber = abs(max(df_patchfibers.loc[i, "stress"], key=abs))
                if stress_max < max_stress_for_one_fiber:
                    stress_max = max_stress_for_one_fiber
                
            # plot patch fiber stresses
            x_list, y_list, z_list = [], [], []
            x_listnode, y_listnode, z_listnode = [], [], []
            hoverinfo_list = []
            color_node = []
            color_line = []
            for i in range(len(df_patchfibers)):
                xc, zc = df_patchfibers.loc[i, "centroid"]
                stresses = df_patchfibers.loc[i, "stress"]
                strains = df_patchfibers.loc[i, "strain"]
                fid = df_patchfibers.loc[i, "tag"]
                strain = strains[STEP]
                stress = stresses[STEP]
                
                if not math.isclose(stress, 0): # do not plot inactive fibers
                    color_raw = df_patchfibers.loc[i, "color_list"]
                    color = color_raw[STEP]
                        
                    u = stress / stress_max * u_max
                    
                    x_list+=[xc, xc, None]
                    y_list+=[0, u, None]
                    z_list+=[zc, zc, None]
                    color_line+=[color,color,"rgba(255, 255, 255, 0)"]
                    
                    x_listnode+=[xc]
                    y_listnode+=[u]
                    z_listnode+=[zc]
                    color_node+=[color]
                    
                    hoverinfo = (
                         "<b>Patch Fiber {:.0f}</b><br>".format(fid) +
                         "<b>x, y</b>: ({:.2f}, {:.2f}) <br>".format(xc, zc) +
                         "<b>strain</b>: {:.2e} <br>".format(strain) +
                         "<b>stress</b>: {:.2f}<br>".format(stress)
                                 )
                    hoverinfo_list.append(hoverinfo)
                
        # NODES
        if node_fiber_exists:
            for i in range(len(df_nodefibers)):
                xc = df_nodefibers.loc[i, "x"] 
                zc = df_nodefibers.loc[i, "y"]
                
                stresses = df_nodefibers.loc[i, "stress"]
                strains = df_nodefibers.loc[i, "strain"]
                fid = df_nodefibers.loc[i, "tag"]
                strain = strains[STEP]
                stress = stresses[STEP]
                
                if not math.isclose(stress, 0): # do not plot inactive fibers
                    color_raw = df_nodefibers.loc[i, "color_list"]
                    color = color_raw[STEP]
                        
                    if stress > 0:
                        u = min(stress/stress_max * u_max, u_max*2)
                    else:
                        u = max(stress/stress_max * u_max, -u_max*2)
                    
                    x_list+=[xc, xc, None]
                    y_list+=[0, u, None]
                    z_list+=[zc, zc, None]
                    color_line+=[color,color,"rgba(255, 255, 255, 0)"]
                    
                    x_listnode+=[xc]
                    y_listnode+=[u]
                    z_listnode+=[zc]
                    color_node+=[color]
                    
                    hoverinfo = (
                         "<b>Node Fiber {:.0f}</b><br>".format(fid) +
                         "<b>x, y</b>: ({:.2f}, {:.2f}) <br>".format(xc, zc) +
                         "<b>strain</b>: {:.2e} <br>".format(strain) +
                         "<b>stress</b>: {:.2f}<br>".format(stress)
                                 )
                    hoverinfo_list.append(hoverinfo)
                    
        stress_trace = go.Scatter3d(x = x_list, 
                                    y = y_list,
                                    z = z_list,
                                    mode="lines",
                                    line_color=color_line,
                                    line_width=6,
                                    hoverinfo="skip",
                                    showlegend=False)
        stress_tip_trace = go.Scatter3d(x = x_listnode, 
                                        y = y_listnode,
                                        z = z_listnode,
                                        mode="markers",
                                        marker_size=6,
                                        marker_symbol="circle",
                                        marker_color=color_node,
                                        showlegend=False,
                                        text=hoverinfo_list,
                                        hovertemplate=hovertemplate,
                                        hoverlabel_bgcolor="beige",
                                        hoverlabel_bordercolor="black",
                                        hoverlabel_font_color="black",
                                        hoverlabel_font_size=16
                                        )
        if STEP == 0:
            fig.add_trace(stress_trace, row=1, col=1)
            fig.add_trace(stress_tip_trace, row=1, col=1)
        else:
            data.append(stress_trace)
            data.append(stress_tip_trace)
            
            
            
        ################################################
        #  DYNAMIC MOMENT CURVATURE MARKER AND INDICATOR LINES
        ################################################
        phi = mk_results["Curvature"].tolist()[STEP]
        M = mk_results["Moment"].tolist()[STEP]
        mk_trace2 = go.Scatter(x = [phi],
                               y = [M],
                                mode="markers",
                                marker_size = 12,
                                line_color = "blue",
                                showlegend=False,
                                hoverinfo="skip")
        mk_trace3 = go.Scatter(x = [phi, phi, None, 0, phi],
                               y = [0, M, None, M, M],
                                mode="lines",
                                line_color = "blue",
                                line_dash = "dash",
                                showlegend=False,
                                hoverinfo="skip")

        if STEP == 0:
            fig.add_trace(mk_trace2, row=1, col=2)
            fig.add_trace(mk_trace3, row=1, col=2)
        else:
            data.append(mk_trace2)
            data.append(mk_trace3)
        
        # static: mk line, patch mesh, node mesh, invisible scene dot (3 or 4 traces)
        # dynamic: stress line, stress dot, mk indicator dot, mk indicator line (4 traces)
        dynamic_traces = [3,4,5,6] if N_STATIC_TRACES==3 else [4,5,6,7]
        frames.append(go.Frame(data=data, name=str(STEP), traces=dynamic_traces))
        STEP +=1

    # finished compiling frames, add to figure object
    fig.update(frames=frames)


    #############################################
    #  SLIDER SETUP
    #############################################
    sliders = [
        {"steps": [{"args": [[str(k)],
                             {"frame": {"duration": 0, "redraw": True},
                              "mode": "immediate"}
                             ],
                    "label": "",
                    "method": "animate"
                    } for k in range(N_FRAME)
                   ],
         "active": 0,
         "transition": {"duration": 0},
         "x": 0.505,
         "xanchor": "left",
         "len": 0.50,
         "y": -0.04,
         "yanchor": "top"}
    ]
    fig.add_annotation(text = "Load Step:",
                       x=0.52,
                       y=-0.06,
                       xref="paper",
                       yref="paper",
                       showarrow=False,
                       font_size=14)

    fig.update_layout(sliders=sliders)

    # 3D plot: adjust zoom level and default camera position
    fig.update_scenes(camera_eye=dict(x=1.5, y=1.5, z=0.5))


    # 3D plot: change origin to be on the bottom left corner. Also adjust aspect ratio
    fig.update_scenes(xaxis_autorange="reversed",
                      yaxis_range=[u_max*2,-u_max*2],
                      aspectmode="data")

    # 3D plot: hide axes
    fig.update_scenes(xaxis_backgroundcolor="white",
                      yaxis_backgroundcolor="white",
                      xaxis_gridcolor="grey",
                      yaxis_gridcolor="grey",
                      xaxis_gridwidth=0.5,
                      yaxis_gridwidth=0.5,
                      zaxis_visible=False,
                      xaxis_visible=False,
                      yaxis_visible=False)


    # 2D plot: plot background color and hover box style
    fig.update_layout(plot_bgcolor="white",
                      margin_pad=5,
                      hoverlabel_bgcolor="beige",
                      hoverlabel_bordercolor="black",
                      hoverlabel_font_color="black",
                      hoverlabel_font_size=16)

    # 2D plot: axes labels and styling
    fig.update_yaxes(title_text="Moment",
                     gridcolor="lightgrey",
                     zerolinecolor="black",
                     tickformat=",.0f",
                     showspikes=True)
    fig.update_xaxes(title_text="Curvature",
                     gridcolor="lightgrey",
                     zerolinecolor="black",
                     showexponent="all",
                     exponentformat="power",
                     showspikes=True)

    # add fig title and adjust margin
    if math.isclose(section.axial,0):
        title_text = "<b>Fiber Kit - Interactive Moment Curvature Visualization</b>"
    else:
        title_text = "<b>Fiber Kit - Interactive Moment Curvature Visualization</b> (P = {:.1f})".format(section.axial)
        
    fig.update_layout(title=title_text,
                      title_xanchor="center",
                      title_font_size=22,
                      title_x=0.5, 
                      title_y=0.98,
                      title_font_color="black",
                      margin_b=120,
                      paper_bgcolor="white",
                      font_color="black")

    # display figure
    print("Done!")
    fig.show()
    return fig
    

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
    N_frame = len(section.curvature)
    save_dir = os.path.join(section.output_dir, "animate")
    os.makedirs(save_dir)
    
    # check if orthogonal axis moment is significant (>5% of major axis)
    if abs(section.momenty[-1]) > 0.05*abs(section.momentx[-1]):
        plot_minor_axis_moment_too = True
    else:
        plot_minor_axis_moment_too = False
    
    # generate and save each frame
    for i in range(N_frame):  
        print("\t generating frame {}...".format(i+1))
        fig, axs = plt.subplots(1,2,figsize=(16,9),gridspec_kw={'width_ratios':[1,1]})
        
        # plot meshes
        for f in section.node_fibers:
            radius = (f.area/3.1415926)**(0.5)
            axs[0].add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.color_list[i],edgecolor="black",zorder=2))
        for f in section.patch_fibers:
            axs[0].add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.color_list[i],edgecolor="black",zorder=1,lw=0.65))
            
        # for plot with only patches, we need to insert an invisible node otherwise axes limit are messed up
        axs[0].plot([0],[0], markersize=0)
        
        # plot Moment Curvature
        if plot_minor_axis_moment_too:
            axs[1].plot(section.curvature[:i], section.momentx[:i], lw=1.75, c="#435be2", label="MomentX")
            axs[1].plot(section.curvature[:i], section.momenty[:i], lw=1.75, c="#435be2", linestyle="--", label="MomentY")
            axs[1].legend(loc="upper left")
            axs[1].set_ylim([min(section.momenty), 1.1*max(section.momentx)])
        else:
            axs[1].plot(section.curvature[:i], section.momentx[:i], lw=1.75, c="#435be2", label="MomentX")
            axs[1].set_ylim([0, 1.1*max(section.momentx)])
        
        # formatting
        if math.isclose(section.axial,0):
            fig.suptitle("Moment Curvature Analysis Animation", fontweight="bold", fontsize=18)
        else:
            fig.suptitle("Moment Curvature Analysis Animation (P = {:.1f})".format(section.axial), fontweight="bold", fontsize=18)
        axs[0].grid(False)
        axs[0].set_axisbelow(True)
        axs[0].set_aspect('equal', 'box')
        
        axs[1].set_xlim(0, max(section.curvature)*1.1)
        axs[1].grid(linewidth=0.75, color="lightgray")
        axs[1].axhline(0, color='black')
        axs[1].axvline(0, color='black')
        axs[1].set_xlabel("Curvature", fontsize=12)
        axs[1].set_ylabel("Moment", fontsize=12)
        plt.tight_layout()
        
        filename = os.path.join(save_dir,"frame{:04d}.png".format(i))
        fig.savefig(filename)
        plt.close(fig)
    
    print("Done! pngs in the result folder may be compiled into gif with tools such as ImageMagick.")
        

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
        axs[0].add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.default_color,edgecolor="black",zorder=1,lw=0.65))
    
    # for plot with only patches, we need to insert an invisible node otherwise axes limit are messed up
    axs[0].plot([0],[0], markersize=0)
    
    # formatting
    fig.suptitle("PM Interaction Diagram (ACI 318-19)", fontweight="bold", fontsize=18)
    axs[0].grid(False)
    axs[0].set_aspect('equal', 'box')
    axs[1].xaxis.set_major_locator(MaxNLocator(nbins=12))
    axs[1].yaxis.set_major_locator(MaxNLocator(nbins=12))

    # plot nominal interaction surface
    # indices: [P,Mx,NA_depth,My,resistance_factor,phi_P,phi_Mx,phi_My]
    M0 = [x for x in section.PM_surface[0][1]]
    P0 = [-x for x in section.PM_surface[0][0]]  # flipped sign so +P is compression
    M180 = [x for x in section.PM_surface[180][1]]
    P180 = [-x for x in section.PM_surface[180][0]] # flipped sign so +P is compression
    axs[1].plot(M0, P0, label="Nominal",linestyle="-",c="blue", marker=None)
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
    axs[1].plot(M0_factored, P0_factored, label="Factored", linestyle="-", c="red")
    axs[1].plot(M180_factored, P180_factored, linestyle="-", c="red")
    
    # plot peak above 0.8Po with dotted line
    M0_factored_top = [x for x in section.PM_surface[0][6][split_index-1:]]
    P0_factored_top = [-x for x in section.PM_surface[0][5][split_index-1:]]
    M180_factored_top = [x for x in section.PM_surface[180][6][split_index-1:]]
    P180_factored_top = [-x for x in section.PM_surface[180][5][split_index-1:]]
    axs[1].plot(M0_factored_top, P0_factored_top, linestyle="--",c="red")
    axs[1].plot(M180_factored_top, P180_factored_top, linestyle="--",c="red")
    
    # plot demands
    P = [] if P==None else P
    M = [] if M==None else M
    axs[1].scatter(M, P, c="red", marker="x",linewidth=1.5, s=100)
    
    # styling
    axs[1].grid(linewidth=0.75, color="lightgray")
    axs[1].axhline(0, color='black')
    axs[1].axvline(0, color='black')
    axs[1].set_xlabel("Moment", fontsize=12)
    axs[1].set_ylabel("Axial Force", fontsize=12)
    axs[1].legend(loc="best")
    plt.tight_layout()
    
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
    fig = plt.figure(figsize=(16,9))
    gs = fig.add_gridspec(2,2)
    axs1 = fig.add_subplot(gs[:, 0])
    axs2 = fig.add_subplot(gs[0, 1])
    axs3 = fig.add_subplot(gs[1, 1], sharex=axs2)
    
    # plot meshes
    for f in section.node_fibers:
        radius = (f.area/3.1415926)**(0.5)
        axs1.add_patch(patches.Circle(f.coord,radius=radius,facecolor=f.color_list[-1],edgecolor="black",zorder=2))
    for f in section.patch_fibers:
        axs1.add_patch(patches.Polygon(np.array(f.vertices),closed=True,facecolor=f.color_list[-1],edgecolor="black",zorder=1,lw=0.65))
        
    # check if orthogonal axis moment is significant (>5% of major axis)
    if abs(section.momenty[-1]) > 0.05*abs(section.momentx[-1]):
        plot_minor_axis_moment_too = True
    else:
        plot_minor_axis_moment_too = False
        
        
    # plot moment curvature
    if plot_minor_axis_moment_too:
        M_resultant = [math.sqrt(x*x + y*y) for x,y in zip(section.momentx, section.momenty)]
        axs2.plot(section.curvature, section.momentx, lw=1.75, c="#435be2", linestyle="--", label="MomentX")
        axs2.plot(section.curvature, section.momenty, lw=1.75, c="#435be2", linestyle=":", label="MomentY")
        axs2.plot(section.curvature, M_resultant, lw=3, c="#435be2", label="Resultant")
        axs2.legend(loc="best")
    else:
        axs2.plot(section.curvature, section.momentx, lw=1.75, c="#435be2", label="MomentX")
        axs2.set_ylim([0, 1.1*max(section.momentx)])
        
        
    
    # plot cracked moment of inertia
    I_ratio = [min(1, I/section.Ig) for I in section.Icr]
    axs3.plot(section.curvature, I_ratio, lw=1.75, c="#435be2")
    
    # plot centroid
    axs1.scatter(section.xc_cracked[-1], section.yc_cracked[-1], c="red", marker="x",linewidth=2, s=240, zorder=3)
    
    # formatting
    if math.isclose(section.axial,0):
        fig.suptitle("Cracked Moment of Inertia Analysis", fontweight="bold", fontsize=18)
    else:
        fig.suptitle("Cracked Moment of Inertia Analysis (P = {:.1f})".format(section.axial), fontweight="bold", fontsize=18)
    axs1.grid(False)
    axs1.set_aspect('equal', 'box')
    
    axs2.grid(linewidth=0.75, color="lightgray")
    axs2.axhline(0, color='black')
    axs2.axvline(0, color='black')
    axs2.set_ylabel("Moment", fontsize=12)
    
    axs3.grid(linewidth=0.75, color="lightgray")
    axs3.axhline(0, color='black')
    axs3.axvline(0, color='black')
    axs3.set_ylabel("Icr / Ig", fontsize=12)
    axs3.set_xlabel("Curvature", fontsize=12)
    axs3.set_xlim([0, 1.1*max(section.curvature)])
    axs3.set_ylim([0,1.1])
    
    plt.tight_layout()
    return fig

    





