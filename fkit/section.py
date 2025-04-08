import numpy as np
import pandas as pd
import math
import itertools
import os
import copy
import time


class Section:
    """
    Fiber kit Section object definition.
    
    Args:
        None
    
    Public Methods:
        Section.add_bar()
        Section.add_bar_group()
        Section.add_patch()
        Section.mesh()
        Section.run_moment_curvature()
        Section.calculate_Icr()
        Section.run_PM_interaction()
        Section.export_data()
    """
    def __init__(self):
        # fiber section object paramters
        self.patch_fibers = []              # list of patch fiber objects in section (usually concrete fibers)
        self.node_fibers = []               # list of node fiber objects in section (usually rebar)
        self.N_bar = 0                      # total number of node fibers in section
        self.N_fiber = 0                    # total number of patch fibers in section
        self.area = None                    # total area of all patch fibers
        self.centroid = None                # geometric centroid of section (x, y)
        self.ymax = None                    # max y coordinate of any fiber (used to determine fiber depth)
        self.depth = None                   # total depth of section (dimension in y)
        
        # moment curvature parameters
        self.curvature = []                 # list of curvature at each load step
        self.neutral_axis = []              # list of neutral axis depth at each load step
        self.momentx = []                   # list of major-axis moment at each load step
        self.momenty = []                   # list of minor-axis moment at each load step (0 for symmetric sections)
        self.K_tangent = []                 # list of moment-curvature tangent slope at each load step
        self.axial = 0                      # user-specified axial force for moment-curvature analysis
        self.df_MK_results = None           # dataframe containing all moment curvature analysis results
        self.Ig = None                      # gross moment of inertia (ignoring all node fibers)
        self.Icr = None                     # list of cracked moment of inertia at each load step
        self.xc_cracked = None              # x centroid at each load step (cracked fibers are removed)
        self.yc_cracked = None              # y centroid at each load step (cracked fibers are removed)
        
        # PM interaction surface parameters
        self.PM_surface = {}                # dictionary of PM interaction surface points
                                                # key = degrees from 0 to 360 (right now only 0 and 180), 
                                                # value = [[P], [Mx], [NA_depth], [My], [resistance_factor], [phi_P], [phi_Mx], [phi_My]]
        self.df_PM_results = None           # dataframe containing all PM interaction analysis results
        
        # other parameters
        self.MK_solved = False              # boolean to see if moment curvature analysis has been conducted
        self.PM_solved = False              # boolean to see if PM interaction analysis has been conducted
        self.Icr_solved = False             # boolean to see if Icr analysis has been conducted
        self.folder_created = False         # boolean to see if export folder has already been created
        self.output_dir = None              # path where export data will be stored   
    
    
    def add_bar(self, coord, area, fiber):
        """
        Add a single rebar at specified location.
        
        Args:
            coord       (float):: coordinate of node fiber (x, y)
            area        float:: area of node fiber
            fiber       NodeFiber:: fiberkit node fiber object
            
        Return:
            None
        """
        copied_fiber = copy.deepcopy(fiber)
        copied_fiber.coord = coord
        copied_fiber.area = area
        copied_fiber.tag = self.N_bar
        self.node_fibers.append(copied_fiber)
        self.N_bar += 1

    
    def add_bar_group(self, xo, yo, b, h, nx, ny, area, perimeter_only, fiber):
        """
        Add a retangular array of rebar.
        
        Args:
            xo                  float:: x coordinate of bottom left corner
            yo                  float:: y coordinate of bottom left corner
            b                   float:: width of rebar array
            h                   float:: height of rebar array
            nx                  int:: number of rebar in x
            ny                  int:: number of rebar in y
            area                float:: cross sectional area of rebar
            perimeter_only      bool:: True or False. Have rebar on perimeter only or fill full array
            fiber               NodeFiber:: fiber kit NodeFiber object
            
        Return:
            None
        """
        # determine spacing
        sx = 0 if nx==1 else b / (nx-1)
        sy = 0 if ny==1 else h / (ny-1)
        
        # generate rebar coordinate
        xcoord=[]
        ycoord=[]
        xcoord.append(xo)
        ycoord.append(yo)
        if sx != 0:
            for i in range(nx-1):
                xcoord.append(xcoord[-1]+sx)
        if sy !=0:
            for i in range(ny-1):
                ycoord.append(ycoord[-1]+sy)
        rebar_coord = list(itertools.product(xcoord,ycoord))
        
        # remove middle bars if in perimeter mode
        if perimeter_only:
            x_edge0=xo
            x_edge1=xcoord[-1]
            y_edge0=yo
            y_edge1=ycoord[-1]
            rebar_coord = [e for e in rebar_coord if e[0]==x_edge0 or e[0]==x_edge1 or e[1]==y_edge0 or e[1]==y_edge1]
        
        # add rebar
        for coord in rebar_coord:
            self.add_bar(coord, area, fiber)
    
    
    def add_patch(self, xo, yo, b, h, nx, ny, fiber):
        """
        Add patch fibers to a specified area.
        
        Args:
            xo          float:: x coordinate of lower left corner
            yo          float:: y coordinate of lower left corner
            b           float:: width
            h           float:: height
            nx          int:: number of fibers along width
            ny          int:: number of fibers along height
            fiber       PatchFiber:: fiberkit PatchFiber object
            
        Return:
            None
        """
        # generate patch vertices
        patch_vertices = []
        dx = b / nx 
        dy = h / ny
        for i in range(nx):
            for j in range(ny):
                xref = xo + i * dx
                yref = yo + j * dy
                node1 = [xref   , yref]
                node2 = [xref+dx, yref]
                node3 = [xref+dx, yref+dy]
                node4 = [xref   , yref+dy]
                patch_vertices.append([node1,node2,node3,node4,node1])
        
        # generate patch fibers
        for vertices in patch_vertices:
            copied_fiber = copy.deepcopy(fiber)
            copied_fiber.vertices = vertices
            copied_fiber.tag = self.N_fiber
            try:
                copied_fiber.find_geometric_properties()
            except:
                raise RuntimeError("ERROR: A node fiber has been assigned to an area. Please redefine with patch fiber.")
            self.patch_fibers.append(copied_fiber)
            self.N_fiber += 1
        
    
    def mesh(self, rotate=0):
        """
        Finalize section definition. Calculate section properties and updates fiber locations with respect to section.
        
        Args:
            rotate       (OPTIONAL) float:: rotates the section by an angle counter clockwise (in degrees). Default = 0
            
        Return:
            None
        """
        # find centroid using first moment of area equation
        sumA=sum([a.area for a in self.patch_fibers])
        xA=sum([a.area*a.centroid[0] for a in self.patch_fibers])
        yA=sum([a.area*a.centroid[1] for a in self.patch_fibers])
        self.area = sumA
        self.centroid = [xA/sumA, yA/sumA]

        # rotate section
        rad = rotate * math.pi / 180
        T = np.array([
            [math.cos(rad), -math.sin(rad)],
            [math.sin(rad), math.cos(rad)]
            ])
        self.centroid = T @ self.centroid
        self.centroid = list(self.centroid)
        for f in self.patch_fibers:
            f.centroid = T @ f.centroid
            for i in range(len(f.vertices)):
                f.vertices[i] = T @ f.vertices[i]
        for f in self.node_fibers:
            f.coord = T @ f.coord
        
        # update depth
        y = []
        for f in self.patch_fibers:
            for nodes in f.vertices:
                y.append(nodes[1])
        ymax=max(y)
        ymin=min(y)
        self.ymax = ymax
        self.depth = ymax - ymin
            
        # update fiber location
        for f in self.patch_fibers:
            f.update_location(self.centroid, self.ymax)
        for f in self.node_fibers:
            f.update_location(self.centroid, self.ymax)
    
    
    def run_moment_curvature(self, phi_target, P=0, N_step=100, show_progress=False):
        """
        Start moment curvature analysis.
        
        Args:
            phi_target (float):
                The moment curvature analysis proceed until thsi target curvature. Please note curvature is
                unit dependent (i.e. 1/in vs. 1/mm). A good starting point is to estimate yield curvature:
                    phi_yield ~= ecu / (1-j)d ~= 0.003 / 0.25d
                    example: 24 in deep section => 0.003 / (0.25)24 = 5.0 e-4      1/in
                    example: 600 mm deep section => 0.003 / (0.25)600 = 2.0 e-5    1/mm
                    
            (OPTIONAL) P = 0 (float):
                applied axial load (-ve is compression)
                
            (OPTIONAL) N_step = 100 (int):
                number of data points to reach phi_target. Size of curvature increment.
            
            (OPTIONAL) show_progress = False (bool):
                whether or not to print out status of moment curvature run

        Return:
            df_results (DataFrame):
                a dataframe containing results of the moment curvature analysis
                                
        Algorithm:
            0.) slowly increment curvature from 0 to an user-specified limit
            1.) at each curvature, use secant method to search for the depth of neutral axis
            2.) neutral axis depth is correct when force equilibrium is established
                2b.) for each fiber:
                        calculate fiber depth with respect to top of section
                        calculate fiber strain based on NA depth and curvature
                        calculate fiber stress based on fiber stress-strain relationship
                        calculate fiber force contribution = stress * area
                        calculate fiber moment contribution = force * distance from fiber to section centroid
                2c.) neural axis depth is found if:
                        sum(fiber_force) + P = 0
            3.) at the correct NA depth, sum moment about section centroid
                    moment = sum(fiber_moment)
            4.) record this point (phi,M) and move to next curvature increment, loop until phi_max
        
        Note:
            For asymmetric sections (including asymmetrically reinforced sections), some minor-axis moment may develop. 
            This is because orientation of neutral axis is not always equal to orientation of applied moment vector. 
            As curvature increases, some minor-axis moment must develop to maintain equilibrium and to keep the 
            neutral-axis in the same user-specified orientation.
        """
        # use root finding algorithm to find neutral axis depth
        self.axial = P
        phi_list = np.linspace(0, phi_target, num=N_step)
        
        time_start = time.time()
        step = 0
        x0 = self.depth/2
        for curvature in phi_list:
            if step == 0:
                # cannot find root when curvature is 0 or close to 0. Insert blanks
                self.curvature.append(0)
                self.neutral_axis.append(0)
                self.momentx.append(0)
                self.momenty.append(0)
                self.K_tangent.append(0)
                for f in self.patch_fibers:
                    f.color_list.append(f.default_color)
                    f.strain.append(0)
                for f in self.node_fibers:
                    f.color_list.append(f.default_color)
                    f.strain.append(0)
            else:
                root = self.secant_method(self.verify_equilibrium, args=curvature, x0=x0, x1=x0+0.1)
                correct_NA = root
                
                sumMx = 0
                sumMy = 0
                for f in self.patch_fibers:
                    F,Mx,My = f.update(curvature,correct_NA,solution_found=True)
                    sumMx += Mx
                    sumMy += My
                for f in self.node_fibers:
                    F,Mx,My = f.update(curvature,correct_NA,solution_found=True) 
                    sumMx += Mx
                    sumMy += My
                
                x0 = correct_NA
                if show_progress:
                    print("\tstep {}: N.A found at {:.1f}. curvature = {:.1e}, M = {:.1f}".format(step,correct_NA,curvature,sumMx))
                
                self.curvature.append(curvature)
                self.neutral_axis.append(correct_NA)
                self.momentx.append(sumMx)
                self.momenty.append(sumMy)
                if step == 1:
                    self.K_tangent.append(0)
                else:
                    slope = (self.momentx[-1] - self.momentx[-2])/(self.curvature[-1] - self.curvature[-2])
                    self.K_tangent.append(slope)
                    
            step +=1
            
            
        time_end = time.time()
        self.MK_solved = True
        print("Moment-curvature analysis completed. Elapsed time: {:.2f} seconds\n".format(time_end - time_start))
        
        # compile result dictionary for return
        result_dict = dict()
        result_dict["Curvature"] = self.curvature
        result_dict["Moment"] = self.momentx
        result_dict["NeutralAxis"] = self.neutral_axis
        result_dict["MinorAxisMoment"] = self.momenty
        result_dict["Axial"] = self.axial
        result_dict["Slope"] = self.K_tangent
        self.df_MK_results = pd.DataFrame.from_dict(result_dict)
        return self.df_MK_results.copy()
        
    
    def secant_method(self, func, args, x0, x1, tol=1e-4, max_iteration = 100):
        """
        Helper method for moment curvature analysis. Root-finding via secant method.
        
        Args:
            func                function:: f(x). In our case f(x) = verify_equilibrium(), and x = neutral-axis depth.
            args                float:: additional argument to pass into f(x). In our case = curvature
            x0                  float:: initial value 1 (ideally close to the root)
            x1                  float:: initial value 2 close to x0 
            tol                 (OPTIONAL) float:: tolerance for convergence
            max_iteration       (OPTIONAL) int:: maximum number of interations before stopping
            
        Return:
            x1                  float:: the root (x) where f(x) = 0
        """
        for i in range(max_iteration):
            fx0 = func(x0, args)
            fx1 = func(x1, args)
            
            # stop if converged on root
            if abs(fx1 - fx0) < tol:
                return x1
            
            # otherwise keep iterating
            try:
                x_next = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
            except ZeroDivisionError:
                print("\tError: Division by zero. Secant method failed. Could not converge.")
                return None
            x0, x1 = x1, x_next

        print("\tWarning: Maximum number of iterations reached. The method may not have converged.")
        print("\tsumF = {:.2f}".format(func(x1,args)))
        return x1
    
    
    def verify_equilibrium(self, NA, args):
        """
        Helper method for moment curvature analysis. This is the f(x) function passed into secant method.
        
        Args:
            NA              float:: an assumed neutral axis depth
            args            float:: curvature at current load step
        
        Return:
            sumF - P        float:: force summation. Equilibrium is established if equal to zero.
        """
        curvature = args
        P = self.axial
        sumF=0
        for f in self.patch_fibers:
            F,_,_ = f.update(curvature, NA, solution_found=False)
            sumF += F
        for f in self.node_fibers:
            F,_,_ = f.update(curvature, NA, solution_found=False)
            sumF += F
        return sumF - P
    
    
    def get_node_fiber_data(self, tag):
        """
        Get node fiber data from moment curvature anlysis
        
        Args:
            tag         int:: node fiber tag (use fkit.plotter.preview_section(show_tag=True) to see IDs)
            
        Return:
            data_dict   dict:: A dictionary that stores the fiber data. Available keys:
                                data_dict["area"] - area assigned to node fiber
                                data_dict["coord"] - coordinate of fiber (x,y)
                                data_dict["depth"] - depth of fiber with respect to extreme compression fiber
                                data_dict["ecc"] - distance from section centroid to fiber
                                data_dict["fiber type"] - fiber type (e.g. Hognestad)
                                data_dict["stress"] - stress at each load step
                                data_dict["strain"] - strain at each load step
                                data_dict["force"] - force contribution at each load step
                                data_dict["momentx"] - moment about x-axis contribution at each load step
                                data_dict["momenty"] - moment about y-axis contribution at each load step
        """
        strain_history = self.node_fibers[tag].strain
        stress_history = [self.node_fibers[tag].stress_strain(x) for x in strain_history]
        force_history = [self.node_fibers[tag].area * x for x in stress_history]
        momentx_history = [self.node_fibers[tag].ecc[1] * x for x in force_history]
        momenty_history = [self.node_fibers[tag].ecc[0] * x for x in force_history]
        
        data_dict={
            "fiber type":self.node_fibers[tag].name,
            "coord":self.node_fibers[tag].coord,
            "depth":self.node_fibers[tag].depth,
            "ecc":self.node_fibers[tag].ecc,
            "stress":stress_history,
            "strain":strain_history,
            "force":force_history,
            "momentx":momentx_history,
            "momenty":momenty_history
            }
        return data_dict
    
    
    def get_patch_fiber_data(self, location):
        """
        Get patch fiber data from moment curvature anlysis
        
        Args:
            location        str or (float):: location can be "top", "bottom", or a [x,y] coordinate .
                                if "top", data from top-most fiber will be reported (max y)
                                if "bottom", data from bottom-most fiber will be reported (min y)
                                if a user-specified coordinate, the program will find the nearest fiber
        Return:
            data_dict   dict:: A dictionary that stores the fiber data. Available keys:
                                data_dict["area"] - area of patch fiber
                                data_dict["centroid"] - x,y coordinate of patch fiber centroid
                                data_dict["depth"] - depth of node fiber with respect to extreme compression fiber
                                data_dict["ecc"] - distance from section centroid to  fiber
                                data_dict["fiber type"] - fiber type (e.g. Hognestad)
                                data_dict["stress"] - stress at each load step
                                data_dict["strain"] - strain at each load step
                                data_dict["force"] - force contribution at each load step
                                data_dict["momentx"] - moment about x-axis contribution at each load step
                                data_dict["momenty"] - moment about y-axis contribution at each load step
        """
        # find tag of closest fiber
        tag = None
        if location == "top":
            ymax = - math.inf
            for f in self.patch_fibers:
                if f.centroid[1] > ymax:
                    ymax = f.centroid[1]
                    tag = f.tag
        elif location == "bottom":
            ymin = math.inf
            for f in self.patch_fibers:
                if f.centroid[1] < ymin:
                    ymin = f.centroid[1]
                    tag = f.tag
        else:
            try:
                rmin = math.inf
                for f in self.patch_fibers:
                    dx = f.centroid[0] - location[0]
                    dy = f.centroid[1] - location[1]
                    r = math.sqrt(dx*dx + dy*dy)
                    if r < rmin:
                        rmin = r
                        tag = f.tag
            except:
                raise RuntimeError("location can be top, bottom, or a coordinate list [x,y]")
        
        # recover stress, force, moment from strain history
        strain_history = self.patch_fibers[tag].strain
        stress_history = [self.patch_fibers[tag].stress_strain(x) for x in strain_history]
        force_history = [self.patch_fibers[tag].area * x for x in stress_history]
        momentx_history = [self.patch_fibers[tag].ecc[1] * x for x in force_history]
        momenty_history = [self.patch_fibers[tag].ecc[0] * x for x in force_history]
        
        data_dict = {
            "fiber type":self.patch_fibers[tag].name,
            "centroid":self.patch_fibers[tag].centroid,
            "area":self.patch_fibers[tag].area,
            "depth":self.patch_fibers[tag].depth,
            "ecc":self.patch_fibers[tag].ecc,
            "stress":stress_history,
            "strain":strain_history,
            "force":force_history,
            "momentx":momentx_history,
            "momenty":momenty_history
            }
        return data_dict

    
    def calculate_Icr(self, Es, Ec):
        """
        Calculate cracked moment of inertia (Icr) at each load step. This method can only
        be called after a successful moment curvature analysis.
        
        This function only makes sense in the context of a reinforced concrete sections.
        Please specify Ec and Es of the concrete and steel material. All patch fibers
        are assumed to be concrete, and all node fibers are assumed to be rebar.
        
        Args:
            Es                  float:: rebar steel Young's modulus
            Ec                  float:: concrete material Young's modulus
        
        Return:
            df_results          (DataFrame)::a result dataframe summarizing Icr at each load step
        
        Note:
            Moment of inertia integral is numerically approximated by a summation.
            For best accuracy. Please mesh your section as fine as possible.
        """
        # exit if no moment curvature data
        if not self.MK_solved:
            print("ERROR: Please run a moment curvature analysis first!")
            return None
        
        # gross moment of inertia (without considering node fibers)
        Ig = 0
        for f in self.patch_fibers:
            A = f.area
            y = f.ecc[1]
            b = max([coord[0] for coord in f.vertices]) - min([coord[0] for coord in f.vertices])
            h = max([coord[1] for coord in f.vertices]) - min([coord[1] for coord in f.vertices])
            Ig += b*h*h*h/12 + A*y*y
        self.Ig = Ig
        
        # compute cracked moment of inertia at each load step
        ns = Es / Ec
        Icr = [Ig]
        x_centroid = [self.centroid[0]]
        y_centroid = [self.centroid[1]]
        for i in range(1, len(self.curvature)): # skip first step with 0 curvature
            x_list = []
            y_list = []
            A_list = []
            dy_list = []
            
            # loop through node fibers
            for f in self.node_fibers:
                A_list.append(f.area * ns) # technically need to multiply by ns-1 for compression steel. Refine later.
                x_list.append(f.ecc[0])
                y_list.append(f.ecc[1])
                
            # loop through each patch fiber (only record if stress != 0)
            for f in self.patch_fibers:
                strain = f.strain[i]
                stress = f.stress_strain(strain)
                if not math.isclose(stress, 0):
                    A_list.append(f.area)
                    x_list.append(f.ecc[0])
                    y_list.append(f.ecc[1])
                
            # calculate current centroid after cracking
            xc = sum([-x*A for x,A in zip(x_list, A_list)]) / sum(A_list)
            yc = sum([-y*A for y,A in zip(y_list, A_list)]) / sum(A_list)
            x_centroid.append(xc)
            y_centroid.append(yc)
            
            # calculate Icr
            dy_list = [y + (yc - self.centroid[1]) for y in y_list]
            Icr_current = sum([y*y*A for y,A in zip(dy_list, A_list)])
            Icr.append(Icr_current)
        
        # save results
        self.Icr = Icr
        self.xc_cracked = x_centroid
        self.yc_cracked = y_centroid
        self.Icr_solved = True
        self.df_MK_results["Icr"] = self.Icr
        self.df_MK_results["Icr/Ig"] = [min(1, I/self.Ig) for I in self.Icr]
        return self.df_MK_results.copy()


    def run_PM_interaction(self, fpc, fy, Es):
        """
        Start ACI 318 PM interaction analysis. Please note solution is independent of user-specified fiber material 
        as all concrete fibers are converted to rectangular stress block behavior, and all rebars are converted to 
        elastic-perfect-plastic behavior.
        
        Args:
            fpc (float):
                Concrete compressive strength (ksi or MPa).
                Note that Ec is calculated internally. Unit of fpc is inferred.
                    If fpc > 15, assume unit is Mpa and Ec = 4700 * sqrt(fpc)
                    if fpc <= 15, assume unit is ksi and Ec = 57000 * sqrt(fpc*1000) / 1000 
                    
            fy (float):
                Rebar yield strength (ksi or MPa)
                
            Es (float):
                Elastic modulus of rebar (ksi or MPa)
            
        Return:
            df_result (DataFrame):
                A dataframe containing coordinates for the PM interaction surface.
        
        Key ACI 318 Assumptions:
            - for concrete, use rectangular stress block (alpha = 0.85, beta ranges from 0.65 to 0.85)
            - for steel, use elastic-perfect-plastic material
            - assume crushing strain at extreme compression fiber = 0.003
        
        Algorithm:
            0.) set extreme compression fiber strain to 0.003
            1.) increment neutral axis depth (c) from 0 to inf
                    at c = 0, pure tension
                    at c = inf, pure compression
            2.) at each c:
                    calculate compression resultant using rectangular stress block
                    calculate tension from all steel fiber 
                    M = sum(fiber_moment)
                    P = sum(fiber_force)
            3.) back to step 1, assume another c value until c = inf
            4.) repeat step 1-3 with section rotated 180 degrees to get the other side
    
        Note:
            Internally within fkit, the sign convention is +P = tension, -P = compression
            This is opposite of what's commonly used within the concrete design industry.
            For plotting and exporting purposes, the sign on P is flipped. 
            But within this object, the +P = tension convention is followed
        """
        # rectangular stress block parameter per ACI
        alpha = 0.85
        
        # calculate beta
        is_imperial_unit = True if fpc <= 15 else False
        if is_imperial_unit:
            if fpc < 4:
                beta = 0.85
            elif fpc > 8:
                beta = 0.65
            else:
                beta = 0.85 - 0.05*(fpc*1000-4000)/1000
        else: # SI unit
            if fpc < 28:
                beta = 0.85
            elif fpc > 55:
                beta = 0.65
            else:
                beta = 0.85 - 0.05*(fpc-28)/7
        
        # calculate rebar yield strain
        ey = fy / Es
        
        # generate a good distribution of neutral axis depths
        NA_depth = self.get_appropriate_NA(fy, fpc, Es, beta, alpha)
        
        # start PM interaction analysis        
        time_start = time.time()
        self.PM_surface[0] = self.get_PM_data(NA_depth, fpc, fy, Es, ey, alpha, beta)
        self.mesh(rotate=180)
        self.PM_surface[180] = self.get_PM_data(NA_depth, fpc, fy, Es, ey, alpha, beta)
        
        # restore to original position
        self.mesh(rotate=180) 
        self.PM_solved = True
        time_end = time.time()
        print("PM interaction analysis per ACI 318 completed. Elapsed time: {:.2f} seconds\n".format(time_end - time_start))
        
        # compile a result_dict to return
        result_dict = dict()
        result_dict["Rotation"] = [0 for a in self.PM_surface[0][0]] + [180 for a in self.PM_surface[0][0]]
        result_dict["P"] = self.PM_surface[0][0] + self.PM_surface[180][0]
        result_dict["Mx"] = self.PM_surface[0][1] + self.PM_surface[180][1]
        result_dict["My"] = self.PM_surface[0][3] + self.PM_surface[180][3]
        result_dict["NeutralAxis"] = self.PM_surface[0][2] + self.PM_surface[180][2]
        result_dict["ResistanceFactor"] = self.PM_surface[0][4] + self.PM_surface[180][4]
        result_dict["P_factored"] = self.PM_surface[0][5] + self.PM_surface[180][5]
        result_dict["Mx_factored"] = self.PM_surface[0][6] + self.PM_surface[180][6]
        result_dict["My_factored"] = self.PM_surface[0][7] + self.PM_surface[180][7]
        self.df_PM_results = pd.DataFrame.from_dict(result_dict)
        
        return self.df_PM_results.copy()
        
           
    def get_appropriate_NA(self, fy, fpc, Es, beta, alpha):
        """
        Helper method called in run_PM_interaction. Essentially this helps distribute the points
        along the interaction curve better. Generate neutral axis depths in 4 distinct regions
            1. pure tension to pure bending
            2. pure bending to fs = fy
            3. fs=fy to fs=0
            4. fs=0 to pure compression
        """
        # find rebar with largest depth
        greatest_depth = 0
        for f in self.node_fibers:
            if f.depth > greatest_depth:
                greatest_depth = f.depth
        
        # c where fs = fy
        ey = fy / Es
        c_fsfy = (0.003)/(0.003+ey) * greatest_depth
        
        # c where fs = 0
        c_fs0 = greatest_depth
        
        # c where section in pure bending
        # root finding usually can't get exactly 0 due to fineness of mesh
        # instead, let's interpolate linearly P and NA
        def root_func(c_guess):
            sumF=0
            for f in self.patch_fibers:
                F,_,_ = f.interaction_ACI(beta*c_guess, alpha*fpc) 
                sumF += F
            for f in self.node_fibers:
                F,_,_ = f.interaction_ACI(c_guess, fy, fpc, Es) 
                sumF += F
            return sumF
        
        increment = self.depth/100
        is_net_tension = True
        c_list = []
        P_list = []
        c_current = increment
        while is_net_tension:
            P = root_func(c_current)
            P_list.append(P)
            c_list.append(c_current)
            c_current += increment
            if P < 0:
                is_net_tension = False
        
        c_pure_bending = c_list[-2] + (c_list[-1] - c_list[-2])/(P_list[-2] - P_list[-1]) * P_list[-2]
        
        # create NA points
        NA_depths1 = list(np.linspace(0.01, c_pure_bending, 10))
        NA_depths2 = list(np.linspace(c_pure_bending, c_fsfy, 10))
        NA_depths3 = list(np.linspace(c_fsfy, c_fs0, 10))
        NA_depths4 = list(np.linspace(c_fs0, 1.25*self.depth, 5))
        NA_depth = NA_depths1 + NA_depths2 + NA_depths3 + NA_depths4 + [3*self.depth]
        return NA_depth
    
    
    def get_PM_data(self, NA_depth, fpc, fy, Es, ey, alpha, beta):
        """
        Helper method used during PM Interaction analysis. Called by run_PM_interaction()
        to get (P, Mx, My) points at various neutral axis depths.
        """
        P = []
        Mx = []
        My = []
        resistance_factor = []
        for c in NA_depth:
            sumF = 0
            sumMx = 0
            sumMy = 0
            greatest_depth = 0
            for f in self.patch_fibers:
                F,Mxi,Myi = f.interaction_ACI(beta*c, alpha*fpc) 
                sumF += F
                sumMx += Mxi
                sumMy += Myi
            for f in self.node_fibers:
                F,Mxi,Myi = f.interaction_ACI(c, fy, fpc, Es) 
                sumF += F
                sumMx += Mxi
                sumMy += Myi
                if f.depth > greatest_depth:
                    greatest_depth = f.depth
            
            # calculate phi factor per ACI
            et = 0.003*(greatest_depth - c)/c
            
            if et>=ey+0.003:
                phi = 0.9
            elif et>=ey and et<ey+0.003:
                phi = 0.75 + 0.15*(et-ey)/((ey+0.003)-ey)
            elif et<ey:
                phi = 0.65
                
            P.append(sumF)
            Mx.append(sumMx)
            My.append(sumMy)
            resistance_factor.append(phi)
            
        phi_P = [a*b for a,b in zip(resistance_factor,P)]
        phi_Mx = [a*b for a,b in zip(resistance_factor,Mx)]
        phi_My = [a*b for a,b in zip(resistance_factor,My)]
        
        return [P,Mx,NA_depth,My,resistance_factor, phi_P, phi_Mx, phi_My]
        
        
    def create_output_folder(self, result_folder):
        """
        Helper method to create folder in current working directory. Called by export_data()
        
        Args:
            result_folder       str:: name of folder to create
            
        Return:
            None
        """
        parent_dir = os.getcwd()
        
        # check if path exists. Handle errors and mkdir if needed
        if os.path.isdir(result_folder):
            folderexists = result_folder
            j=1
            while os.path.isdir(result_folder):
                result_folder = folderexists + str(j)
                j=j+1
            output_dir = os.path.join(parent_dir,result_folder)
            os.makedirs(output_dir)
            print("Results to be exported to folder: {}".format(output_dir))
        else:
            output_dir = os.path.join(parent_dir,result_folder)
            os.makedirs(output_dir)
            print("Results to be exported to folder: {}".format(output_dir))
        
        self.folder_created = True
        self.output_dir = output_dir
        
    
    def export_data(self, save_folder = "exported_data_fkit"):
        """
        Export data in csv format in a save_folder which will be created in the user current working directory.
        
        Args:
            save_folder     (OPTIONAL) str:: default folder name = "exported_data_fkit"
            
        Return:
            None
        """
        # create folder
        if not self.folder_created:
            self.create_output_folder(result_folder=save_folder)
        
        # export data to csv
        if self.MK_solved:
            filename = os.path.join(self.output_dir, "moment_curvature.csv")
            self.df_MK_results.to_csv(filename)
            
        if self.PM_solved:
            filename = os.path.join(self.output_dir, "interaction.csv")
            self.df_PM_results.to_csv(filename)
                



