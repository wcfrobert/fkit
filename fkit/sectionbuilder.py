"""
SectionBuilder.

functions to parametrically define commonly used sections
"""
import fkit.section
import math
import numpy as np
import pandas as pd
import os




def rectangular(width, height, cover, top_bar, bot_bar, concrete_fiber, steel_fiber, 
                mesh_nx=0.5, mesh_ny=0.5):
    """
    rectangular section
        width           width of section
        height          height of section
        cover           cover to bar centroid
        top_bar         top bar [bar_area, nx, ny, y_spacing]. Set to None for no rebar
                            example: [0.6, 3, 1, 0] = 3 bars with 0.6 in^2 area in top layer
        bot_bar         bot bar [bar_area, nx, ny, y_spacing]. Set to None for no rebar
                            example: [0.6, 4, 2, 3] = two rows of 4 bars (8 total) with 0.6 in^2 area separated by a vertical distance of 3 in

        concrete_fiber  patch fiber object for concrete
        steel_fiber     node fiber object for steel rebar

        mesh_nx         mesh density in the x direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
        mesh_ny         mesh density in the y direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()

    # parameters used to create square mesh
    n_baseline = 36
    L_baseline = height
    nx_concrete = (n_baseline/L_baseline) * width
    ny_concrete = n_baseline
    

    # concrete fibers
    sec.add_patch(xo=-0.5*width, yo=-0.5*height, b=width ,h=height, 
                  nx=math.ceil(nx_concrete * mesh_nx), ny=math.ceil(ny_concrete * mesh_ny), fiber=concrete_fiber)
    
    # create bars
    if top_bar != None:
        sec.add_bar_group(xo=-(0.5*width-cover), yo=(0.5*height-cover)- top_bar[3],
                          b=(width-2*cover), h=top_bar[3], nx=top_bar[1], ny=top_bar[2], area=top_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
    
    if bot_bar != None:
        sec.add_bar_group(xo=-(0.5*width-cover), yo=-(0.5*height-cover),
                          b=(width-2*cover), h=bot_bar[3], nx=bot_bar[1], ny=bot_bar[2], area=bot_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
    sec.mesh()
    return sec



def rectangular_confined(width, height, cover, top_bar, bot_bar,
                         core_fiber, cover_fiber, steel_fiber, 
                         mesh_nx=0.5, mesh_ny=0.5):
    """
    rectangular section with unconfined cover and a confined core.
        width           width of section
        height          height of section
        cover           cover to bar centroid
        top_bar         top bar [bar_area, nx, ny, y_spacing]. Set to None for no rebar
                            example: [0.6, 3, 1, 0] = 3 bars with 0.6 in^2 area in top layer
        bot_bar         bot bar [bar_area, nx, ny, y_spacing]. Set to None for no rebar
                            example: [0.6, 4, 2, 3] = two rows of 4 bars (8 total) with 0.6 in^2 area separated by a vertical distance of 3 in

        core_fiber      patch fiber object with material properties for the inner core
        cover_fiber     patch fiber object with material properties for the cover
        steel_fiber     node fiber object for steel rebar

        mesh_nx         mesh density in the x direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
        mesh_ny         mesh density in the y direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()
    
    # parameters used to create square mesh
    n_baseline = 36
    L_baseline = height

    nx_core = (n_baseline/L_baseline) * (width - 2*cover)
    ny_core = (n_baseline/L_baseline) * (height - 2*cover)

    nx_sides = (n_baseline/L_baseline) * cover
    ny_sides = n_baseline

    nx_ends = (n_baseline/L_baseline) * (width - 2*cover)
    ny_ends = (n_baseline/L_baseline) * (cover)
    
    # core fibers
    sec.add_patch(xo=-(0.5*width-cover), yo=-(0.5*height-cover), b=(width-2*cover) ,h=(height-2*cover), 
                  nx=math.ceil(nx_core * mesh_nx), ny=math.ceil(ny_core * mesh_ny), fiber=core_fiber)
    
    # left and right cover
    sec.add_patch(xo=-(0.5*width), yo=-(0.5*height), b=cover, h=height, 
                  nx=math.ceil(nx_sides * mesh_nx), ny=math.ceil(ny_sides * mesh_ny), fiber=cover_fiber)
    sec.add_patch(xo=(0.5*width-cover), yo=-(0.5*height), b=cover, h=height, 
                  nx=math.ceil(nx_sides * mesh_nx), ny=math.ceil(ny_sides * mesh_ny), fiber=cover_fiber)
    
    # bottom and top cover
    sec.add_patch(xo=-(0.5*width-cover), yo=-(0.5*height), b=(width-2*cover), h=cover, 
                  nx=math.ceil(nx_ends * mesh_nx), ny=math.ceil(ny_ends * mesh_ny), fiber=cover_fiber)
    sec.add_patch(xo=-(0.5*width-cover), yo=0.5*height-cover, b=(width-2*cover), h=cover, 
                  nx=math.ceil(nx_ends * mesh_nx), ny=math.ceil(ny_ends * mesh_ny), fiber=cover_fiber)
    
    # rebars
    if top_bar != None:
        sec.add_bar_group(xo=-(0.5*width-cover), yo=(0.5*height-cover)- top_bar[3],
                          b=(width-2*cover), h=top_bar[3], nx=top_bar[1], ny=top_bar[2], area=top_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
    
    if bot_bar != None:
        sec.add_bar_group(xo=-(0.5*width-cover), yo=-(0.5*height-cover),
                          b=(width-2*cover), h=bot_bar[3], nx=bot_bar[1], ny=bot_bar[2], area=bot_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
    sec.mesh() 
    return sec




def circular(diameter, cover, N_bar, A_bar, 
             core_fiber, cover_fiber, steel_fiber, mesh_n=0.5):
    """
    circular section. fkit currently only supports rectangular fibers. Here we are
    generating circular section by first generating a square that
    inscribes a circle, then trimming away the four corners.
        diameter        diameter of circular section
        cover           cover to sprial ties
        N_bar           number of bars evenly distributed along perimeter
        A_bar           area of rebar

        core_fiber      patch fiber object with material properties for the inner core
        cover_fiber     patch fiber object with material properties for the cover
        steel_fiber     node fiber object for steel rebar

        mesh_n          mesh density (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()

    n_baseline = 68

    # remove fibers based on radial distance
    r_inner = (diameter - cover*2)/2
    r_outer = diameter/2
    removal_index = []
    
    # generate inner core box
    sec.add_patch(xo=-diameter/2, yo=-diameter/2, b=diameter ,h=diameter, 
                  nx=math.ceil(n_baseline*mesh_n), ny=math.ceil(n_baseline*mesh_n), fiber=core_fiber)

    for i in range(len(sec.patch_fibers)):
        f = sec.patch_fibers[i]
        dx = f.centroid[0]
        dy = f.centroid[1]
        r = math.sqrt(dx*dx + dy*dy)
        if r > r_inner:
            removal_index.append(f.tag)
    last_index = i


    # generate outer cover box overlapping previous patches
    sec.add_patch(xo=-0.5*diameter, yo=-0.5*diameter, b=diameter ,h=diameter, 
                  nx=math.ceil(n_baseline*mesh_n), ny=math.ceil(n_baseline*mesh_n), fiber=cover_fiber)
    
    for i in range(last_index+1, len(sec.patch_fibers)):
        f = sec.patch_fibers[i]
        dx = f.centroid[0]
        dy = f.centroid[1]
        r = math.sqrt(dx*dx + dy*dy)
        if r < r_inner or r > r_outer:
            removal_index.append(f.tag)
    
    # remove extraneous fibers
    for i in sorted(removal_index, reverse=True):
        del sec.patch_fibers[i]
    
    # add rebar
    deg_list = np.linspace(0,360,N_bar+1)
    deg_list = deg_list[:-1]
    for deg in deg_list:
        rad = deg / 180 * math.pi
        x = r_inner*math.cos(rad)
        y = r_inner*math.sin(rad)
        sec.add_bar([x,y], A_bar, steel_fiber)

    sec.mesh()
    return sec




def flanged(bw, bf, h, tf, cover, bot_bar, top_bar, slab_bar,
            core_fiber, cover_fiber, steel_fiber, mesh_nx=0.5, mesh_ny=0.5):
    """
    Beam with effective flange forming a T-beam
        bw              width of web
        bf              width of flange
        h               total height of section
        tf              thickness of slab/flange
        cover           cover to centroid of first bar
        bottom bar      [bar area, nx, ny, s] . Set to None for no rebar
        top bar         [bar area, nx, ny, s]. Set to None for no rebar
                            nx is number of bar layers in x direction
                            ny is the number of bar layer in the y direction
                            s is the spacing between bar layers in the y direction
                            example: [0.6, 3, 1, 0] = 3 bars with 0.6 in^2 area in one layer
                            example: [0.6, 4, 2, 3] = 8 bars with 0.6 in^2 area in two layers with 3 in spacing between layers
        slab bar        [bar area, spacing, ny, s]
                            same as above, but rather than specifying nx, specify a bar spacing in the slab

        core_fiber      patch fiber object with material properties for the inner core
        cover_fiber     patch fiber object with material properties for the cover and slab
        steel_fiber     node fiber object for steel rebar

        mesh_nx         mesh density in the x direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
        mesh_ny         mesh density in the y direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()
    
    # parameters used to create square mesh
    n_baseline = 48
    L_baseline = h

    nx_core = (n_baseline/L_baseline) * (bw - cover*2)
    ny_core = (n_baseline/L_baseline) * (h - cover*2)

    nx_sides = (n_baseline/L_baseline) * cover
    ny_sides =(n_baseline/L_baseline) * h

    nx_ends = (n_baseline/L_baseline) * bw
    ny_ends = (n_baseline/L_baseline) * cover

    nx_slab = (n_baseline/L_baseline) * (bf-bw)/2
    ny_slab = (n_baseline/L_baseline) * tf
    
    
    # core fibers
    sec.add_patch(xo=-bw/2+cover, yo=cover, b=bw-2*cover ,h=h-2*cover, 
                  nx=math.ceil(nx_core*mesh_nx), ny=math.ceil(ny_core*mesh_ny), fiber=core_fiber)
    
    # left and right cover
    sec.add_patch(xo=-bw/2, yo=0, b=cover, h=h, 
                  nx=math.ceil(nx_sides*mesh_nx), ny=math.ceil(ny_sides*mesh_ny), fiber=cover_fiber)
    sec.add_patch(xo=bw/2-cover, yo=0, b=cover, h=h, 
                  nx=math.ceil(nx_sides*mesh_nx), ny=math.ceil(ny_sides*mesh_ny), fiber=cover_fiber)
    
    # bottom and top cover
    sec.add_patch(xo=-bw/2+cover, yo=0, b=(bw-2*cover), h=cover, 
                  nx=math.ceil(nx_ends*mesh_nx), ny=math.ceil(ny_ends*mesh_ny), fiber=cover_fiber)
    sec.add_patch(xo=-bw/2+cover, yo=h-cover, b=(bw-2*cover), h=cover, 
                  nx=math.ceil(nx_ends*mesh_nx), ny=math.ceil(ny_ends*mesh_ny), fiber=cover_fiber)
    
    # slab flange
    sec.add_patch(xo=-bf/2, yo=h-tf, b=(bf-bw)/2, h=tf, 
                  nx=math.ceil(nx_slab*mesh_nx), ny=math.ceil(ny_slab*mesh_ny), fiber=cover_fiber)
    sec.add_patch(xo=bw/2, yo=h-tf, b=(bf-bw)/2, h=tf, 
                  nx=math.ceil(nx_slab*mesh_nx), ny=math.ceil(ny_slab*mesh_ny), fiber=cover_fiber)
    
    # rebar
    if top_bar != None:
        sec.add_bar_group(xo=-0.5*bw+cover, yo=h - cover - top_bar[3],
                          b=(bw-2*cover), h=top_bar[3], nx=top_bar[1], ny=top_bar[2], area=top_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
    if bot_bar != None:
        sec.add_bar_group(xo=-0.5*bw+cover, yo=cover,
                          b=(bw-2*cover), h=bot_bar[3], nx=bot_bar[1], ny=bot_bar[2], area=bot_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
    
    if slab_bar != None:
        nx = math.ceil((bf/2-bw/2-cover*2) / slab_bar[1])
        sec.add_bar_group(xo=-0.5*bf+cover, yo=h-tf+cover,
                          b=bf/2-bw/2-cover*2, h=tf-2*cover, nx=nx, ny=slab_bar[2], area=slab_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
        
        sec.add_bar_group(xo=bw/2+cover, yo=h-tf+cover,
                          b=bf/2-bw/2-cover*2, h=tf-2*cover, nx=nx, ny=slab_bar[2], area=slab_bar[0],
                          perimeter_only=False, fiber=steel_fiber)

    sec.mesh()
    return sec





def wall(width, length, cover, wall_bar,
         concrete_fiber, steel_fiber, 
         mesh_nx=0.5, mesh_ny=0.5):
    """
    planar wall without boundary elements
        width               wall width (or thickness)
        length              wall length
        cover               cover to centroid of bar
        wall_bar            rebar along length of wall [bar_area, spacing, layer]. Set to None for no rebar
                                example: [0.6, 12, 2] = 0.6 area bars spaced at 12 inches in two layers

        concrete_fiber      patch fiber object for concrete
        steel_fiber         node fiber object for steel rebar

        mesh_nx             mesh density in the x direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
        mesh_ny             mesh density in the y direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()
    
    # wall patch
    sec.add_patch(xo=-0.5*width, yo=-0.5*length, b=width ,h=length, 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(80*mesh_ny), fiber=concrete_fiber)
    
    # web rebar
    if wall_bar != None:
        ny = math.ceil((length-2*cover) / wall_bar[1])
        sec.add_bar_group(xo=-(0.5*width-cover), yo=-(0.5*length-cover),
                          b=(width-2*cover), h=length-2*cover, nx=wall_bar[2], ny=ny, area=wall_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
    
    sec.mesh()
    return sec





def wall_BE(width, length, cover, BE_length, wall_bar, BE_bar,
            concrete_fiber, BE_fiber, steel_fiber, 
            mesh_nx=0.5, mesh_ny=0.5):
    """
    planar wall with boundary elements
        width               wall width (or thickness)
        length              total wall length including boundary element
        cover               cover to bar centroid
        BE_length           length of boundary elements from end of wall to end of boundary element
        wall_bar            rebar along length of wall [bar_area, spacing, layer]. Set to None for no web rebar
                                example: [0.6, 12, 2] = 0.6 area bars spaced at 12 inches in two layers
        BE_bar              rebar within boundary element [bar_area, nx, ny]. Set to None for no BE rebar
                                example [1.0, 3, 4] = 1.0 area bars forming a rectangular array nx by ny within boundary element
        concrete_fiber      patch fiber object for concrete
        BE_fiber            patch fiber object for BE concrete
        steel_fiber         node fiber object for steel rebar

        mesh_nx             mesh density in the x direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
        mesh_ny             mesh density in the y direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()
    
    # wall patch
    sec.add_patch(xo=-0.5*width, yo=-0.5*length+BE_length, b=width ,h=(length-2*BE_length), 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(80*mesh_ny), fiber=concrete_fiber)
    
    # BE patches
    sec.add_patch(xo=-0.5*width+cover, yo=-0.5*length+cover, b=width-2*cover , h=BE_length-cover, 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(24*mesh_ny), fiber=BE_fiber)
    
    sec.add_patch(xo=-0.5*width+cover, yo=0.5*length-BE_length, b=width-2*cover ,h=BE_length-cover, 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(24*mesh_ny), fiber=BE_fiber)
    
    # top and bottom cover
    sec.add_patch(xo=-0.5*width, yo=-0.5*length, b=width ,h=cover, 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(2*mesh_ny), fiber=concrete_fiber)
    sec.add_patch(xo=-0.5*width, yo=0.5*length-cover, b=width ,h=cover, 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(2*mesh_ny), fiber=concrete_fiber)
    
    # side covers
    sec.add_patch(xo=-0.5*width, yo=-0.5*length+cover, b=cover ,h=BE_length-cover, 
                  nx=math.ceil(2*mesh_nx), ny=math.ceil(14*mesh_ny), fiber=concrete_fiber)
    sec.add_patch(xo=0.5*width-cover, yo=-0.5*length+cover, b=cover ,h=BE_length-cover, 
                  nx=math.ceil(2*mesh_nx), ny=math.ceil(14*mesh_ny), fiber=concrete_fiber)
    
    
    sec.add_patch(xo=-0.5*width, yo=0.5*length-BE_length, b=cover ,h=BE_length-cover, 
                  nx=math.ceil(2*mesh_nx), ny=math.ceil(14*mesh_ny), fiber=concrete_fiber)
    sec.add_patch(xo=0.5*width-cover, yo=0.5*length-BE_length, b=cover ,h=BE_length-cover, 
                  nx=math.ceil(2*mesh_nx), ny=math.ceil(14*mesh_ny), fiber=concrete_fiber)
    
    # web rebar
    if wall_bar != None:
        ny = math.ceil((length-2*cover*4-2*BE_length) / wall_bar[1])
        sec.add_bar_group(xo=-0.5*width+cover, yo=-0.5*length+cover*4+BE_length,
                          b=(width-2*cover), h=(length-2*cover*4-2*BE_length), nx=wall_bar[2], ny=ny, area=wall_bar[0],
                          perimeter_only=False, fiber=steel_fiber)
        
    # BE rebar
    if BE_bar != None:
        sec.add_bar_group(xo=-0.5*width+cover, yo=-0.5*length+cover,
                          b=(width-2*cover), h=BE_length-cover, nx=BE_bar[1], ny=BE_bar[2], area=BE_bar[0],
                          perimeter_only=True, fiber=steel_fiber)
        
        sec.add_bar_group(xo=-0.5*width+cover, yo=0.5*length-BE_length,
                          b=(width-2*cover), h=BE_length-cover, nx=BE_bar[1], ny=BE_bar[2], area=BE_bar[0],
                          perimeter_only=True, fiber=steel_fiber)
        
    sec.mesh()
    return sec





def wall_layered(width1, width2, length, cover, wall_bar1, wall_bar2,
                 concrete_fiber1, concrete_fiber2, steel_fiber1, steel_fiber2,
                 mesh_nx=0.5, mesh_ny=0.5):
    """
    planar wall with two layers (meant to simulate shotcrete walls)
        width1              width of layer 1
        width2              width of layer 2
        length              wall length
        cover               cover to centroid of bar
        wall_bar1           rebar in layer 1 [bar_area, spacing, layer]. Set to None for no rebar
        wall_bar2           rebar in layer 2 [bar_area, spacing, layer]. Set to None for no rebar
                                example: [0.6, 12, 2] = 0.6 area bars spaced at 12 inches in two layers
            
        concrete_fiber1     patch fiber object for concrete layer 1
        concrete_fiber2     patch fiber object for concrete layer 2
        steel_fiber1        node fiber object for steel rebar in layer 1
        steel_fiber2        node fiber object for steel rebar in layer 2
        
        mesh_nx             mesh density in the x direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
        mesh_ny             mesh density in the y direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()
    
    # wall patch
    sec.add_patch(xo=-width1, yo=-0.5*length, b=width1 ,h=length, 
                  nx=math.ceil(8*mesh_nx), ny=math.ceil(60*mesh_ny), fiber=concrete_fiber1)
    sec.add_patch(xo=0, yo=-0.5*length, b=width2 ,h=length, 
                  nx=math.ceil(8*mesh_nx*(width2/width1)), ny=math.ceil(60*mesh_ny), fiber=concrete_fiber2)
    
    # web rebar
    if wall_bar1 != None:
        ny = math.ceil((length-2*cover) / wall_bar1[1])
        sec.add_bar_group(xo=-width1+cover, yo=-(0.5*length-cover),
                          b=width1-2*cover, h=length-2*cover, nx=wall_bar1[2], ny=ny, area=wall_bar1[0],
                          perimeter_only=False, fiber=steel_fiber1)
        
    if wall_bar2 != None:
        ny = math.ceil((length-2*cover) / wall_bar2[1])
        sec.add_bar_group(xo=cover, yo=-(0.5*length-cover),
                          b=width2-2*cover, h=length-2*cover, nx=wall_bar2[2], ny=ny, area=wall_bar2[0],
                          perimeter_only=False, fiber=steel_fiber2)
        
    
    sec.mesh()
    return sec





def wall_speedcore(length, width, steel_thickness,
                   concrete_fiber, steel_fiber, 
                   mesh_nx=0.5, mesh_ny=0.5):
    """
    Also known as concrete-filled composite steel plate shear wall (CF-CPSW).
        length              total length of wall
        width               total width of wall
        steel_thickness     thickness of steel plate confining wall

        concrete_fiber      patch fiber object with material properties for concrete
        steel_fiber         patch fiber object with material properties for steel plate

        mesh_nx             mesh density in the x direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
        mesh_ny             mesh density in the y direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()
    
    
    # core fibers
    sec.add_patch(xo=-(0.5*width-steel_thickness), yo=-(0.5*length-steel_thickness), b=(width-2*steel_thickness) ,h=(length-2*steel_thickness), 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(80*mesh_ny), fiber=concrete_fiber)
    
    # left and right plate
    sec.add_patch(xo=-(0.5*width), yo=-(0.5*length), b=steel_thickness, h=length, 
                  nx=math.ceil(2*mesh_nx), ny=math.ceil(80*mesh_ny), fiber=steel_fiber)
    sec.add_patch(xo=(0.5*width-steel_thickness), yo=-(0.5*length), b=steel_thickness, h=length, 
                  nx=math.ceil(2*mesh_nx), ny=math.ceil(80*mesh_ny), fiber=steel_fiber)
    
    # bottom and top plate
    sec.add_patch(xo=-(0.5*width-steel_thickness), yo=-(0.5*length), b=(width-2*steel_thickness), h=steel_thickness, 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(2*mesh_ny), fiber=steel_fiber)
    sec.add_patch(xo=-(0.5*width-steel_thickness), yo=0.5*length-steel_thickness, b=(width-2*steel_thickness), h=steel_thickness, 
                  nx=math.ceil(14*mesh_nx), ny=math.ceil(2*mesh_ny), fiber=steel_fiber)
    
    sec.mesh() 
    return sec




def wide_flange(bf, d, tw, tf, steel_fiber, mesh_nx=0.5, mesh_ny=0.5):
    """
    creates a wide-flange section
        bf              width of flange
        d               depth
        tw              web thickness
        tf              flange thickness
        steel_fiber     patch fiber object for structural steel
        mesh_nx         mesh density in the x direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
        mesh_ny         mesh density in the y direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
    """
    # create section
    sec = fkit.section.Section()

    # flanges
    sec.add_patch(xo=-bf/2, yo=-d/2, b=bf ,h=tf, 
                  nx=math.ceil(44*mesh_nx), ny=math.ceil(10*mesh_ny), fiber=steel_fiber)
    sec.add_patch(xo=-bf/2, yo=d/2-tf, b=bf ,h=tf, 
                  nx=math.ceil(44*mesh_nx), ny=math.ceil(10*mesh_ny), fiber=steel_fiber)
    
    # web
    sec.add_patch(xo=-tw/2, yo=-d/2+tf, b=tw ,h=d-2*tf, 
                  nx=math.ceil(4*mesh_nx), ny=math.ceil(44*mesh_ny), fiber=steel_fiber)
    
    sec.mesh()
    return sec




def W_AISC(shape, steel_fiber, mesh_nx=0.5, mesh_ny=0.5):
    """
    create wide flange section from AISC wide flange database
        shape           shape designation (e.g. W14X53)
        steel_fiber     patch fiber object for structural steel
        mesh_nx         mesh density in the x direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
        mesh_ny         mesh density in the y direction (0 being least dense, 1 being most dense)
                            OPTIONAL: default = 0.5
    """
    aisc_file = os.path.join(os.path.dirname(__file__), "AISC.csv")
    df_AISC = pd.read_csv(aisc_file)
    df_AISC = df_AISC.set_index("section")
    
    bf = df_AISC.loc[shape]["bf"]
    d = df_AISC.loc[shape]["d"]
    tw = df_AISC.loc[shape]["tw"]
    tf = df_AISC.loc[shape]["tf"]
    
    return wide_flange(bf, d, tw, tf, steel_fiber, mesh_nx, mesh_ny)




def W_AISC_composite(shape, slab_thickness, slab_width, slab_gap, slab_bar, cover,
                     concrete_fiber,steel_fiber,rebar_fiber, mesh_nx=0.5, mesh_ny=0.5):
    """
    create a composite beam with AISC wide flange (experimental)
        shape               shape designation (e.g. W14X53)
        
        slab_thickness      slab thickness
        slab_width          slab effective flange width
        cover               cover to centroid of slab bar
        slab_gap            gap between top of flange and bottom of slab (used for slab on deck)
        slab bar            [bar area, spacing, ny, s]. Set to None for no rebar
                                example: [0.6, 12, 2, 3] = 0.6 area bars spaced at 12 in two layers with 3 spacing between layers
        
        concrete_fiber      patch fiber object with material properties for concrete
        steel_fiber         patch fiber object with material properties for structural steel
        rebar_fiber         node fiber object for steel rebar
        
        mesh_nx             mesh density in the x direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
        mesh_ny             mesh density in the y direction (0 being least dense, 1 being most dense)
                                OPTIONAL: default = 0.5
    """
    # create W fibers
    aisc_file = os.path.join(os.path.dirname(__file__), "AISC.csv")
    df_AISC = pd.read_csv(aisc_file)
    df_AISC = df_AISC.set_index("section")
    
    bf = df_AISC.loc[shape]["bf"]
    d = df_AISC.loc[shape]["d"]
    tw = df_AISC.loc[shape]["tw"]
    tf = df_AISC.loc[shape]["tf"]
    sec = wide_flange(bf, d, tw, tf, steel_fiber, mesh_nx, mesh_ny)
    
    # mesh density
    nx = mesh_nx * 2 + 0.1
    ny = mesh_ny * 2 + 0.1
    
    # create slab fibers
    sec.add_patch(xo=-slab_width/2, yo=d/2+slab_gap, b=slab_width, h=slab_thickness, 
                  nx=math.ceil(slab_width*nx), ny=math.ceil(slab_thickness*ny), fiber=concrete_fiber)
    
    # create rebar
    if slab_bar != None:
        nx = math.ceil((slab_width / slab_bar[1]))
        if slab_bar[2] == 1:
            sec.add_bar_group(xo=-0.5*slab_width+cover, yo=d/2+slab_gap+slab_thickness/2,
                              b=slab_width-2*cover, h=slab_thickness, nx=nx, ny=slab_bar[2], area=slab_bar[0],
                              perimeter_only=True, fiber=rebar_fiber)
        else:
            sec.add_bar_group(xo=-0.5*slab_width+cover, yo=d/2+slab_gap+cover,
                              b=slab_width-2*cover, h=slab_thickness-2*cover, nx=nx, ny=slab_bar[2], area=slab_bar[0],
                              perimeter_only=True, fiber=rebar_fiber)
        
    sec.mesh()  
    return sec











