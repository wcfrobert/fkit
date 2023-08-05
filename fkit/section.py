import numpy as np
import math
#import scipy.optimize as sp
import itertools
import os
import copy
import time



class Section:
    """
    Section object definition:
        patch_fibers                list of patch fiber objects in section (usually concrete fibers)
        node_fibers                 list of node fiber objects in section (usually rebar)
        N_bar                       number of node fibers in section
        N_fiber                     number of patch fibers in section
        area                        total area of all patch fibers
        centroid                    geometric centroid of section
        ymax                        max y coordinate of any fiber (used to determine fiber depth)
        depth                       total depth of section (dimension in y)
        
        MK_solved                   boolean to see if moment curvature analysis has been conducted
        PM_solved                   boolean to see if PM interaction analysis has been conducted
        PM_solved_ACI               boolean to see if ACI PM interaction analysis has been conducted
        folder_created              boolean to see if export folder has already been created
        output_dir                  path where export data will be stored   
        
    From moment curvature analysis
        curvature                   list of curvature
        neutral_axis                list of neutral axis depth
        momentx                     list of major-axis moment
        momenty                     list of minor-axis moment (should be 0 for symmetric section)
        K_tangent                   list of moment-curvature tangent slope
        axial                       user-specified axial force for moment-curvature analysis
        
    From interaction surface analysis
        PM_surface                  key = orientation (0 or 180), value = [[P], [M], [NA_depth]]
        PM_surface_ACI              key = orientation (0 or 180), value = [[P], [M], [NA_depth], [phi]]
        PM_surface_ACI_factored     key = orientation (0 or 180), value = [[P_factored], [M_factored], [NA_depth], [phi]]
    """
    def __init__(self):
        self.patch_fibers = []
        self.node_fibers = []
        self.N_bar = 0
        self.N_fiber = 0
        self.area = None
        self.centroid = None
        self.ymax = None
        self.depth = None
        
        self.curvature = []
        self.neutral_axis = []
        self.momentx = []
        self.momenty = []
        self.K_tangent = []
        self.axial = 0
        
        self.PM_surface = {}
        self.PM_surface_ACI = {}
        self.PM_surface_ACI_factored = {}
        
        self.MK_solved = False
        self.PM_solved = False
        self.PM_solved_ACI = False
        self.folder_created = False
        self.output_dir = None
    
    def add_bar(self, coord, area, fiber):
        """add a single rebar at specified location"""
        copied_fiber = copy.deepcopy(fiber)
        copied_fiber.coord = coord
        copied_fiber.area = area
        copied_fiber.tag = self.N_bar
        self.node_fibers.append(copied_fiber)
        self.N_bar += 1

    
    def add_bar_group(self, xo, yo, b, h, nx, ny, area, perimeter_only, fiber):
        """
        Add a retangular array of rebar
            xo = x coordinate of bottom left corner
            yo = y coordinate of bottom left corner
            b = width of rebar group
            h = height of rebar group
            nx = number of rebar in x
            ny = number of rebar in y
            area = cross sectional area of rebar
            perimeter_only = True or False. Have rebar perimeter only or fill
            fiber = node fiber object with material properties
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
        Add patch fibers to a rectangular area
            xo = x coordinate of lower left corner
            yo = y coordinate of lower left corner
            b = width
            h = height
            nx = density of mesh along width
            ny = density of mesh along height
            fiber = patch fiber object with material properties
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
        
        # generate concrete fibers
        for vertices in patch_vertices:
            copied_fiber = copy.deepcopy(fiber)
            copied_fiber.vertices = vertices
            copied_fiber.tag = self.N_fiber
            copied_fiber.find_geometric_properties()
            self.patch_fibers.append(copied_fiber)
            self.N_fiber += 1
        
    
    def mesh(self, rotate=0):
        """Rotate if specified. Calculate some section properties. Update fiber locations"""
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
    
    
    def run_moment_curvature(self, P=0, phi_max=0.0004, N_step=100, show_progress=False):
        """
        Start moment curvature analysis
    
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
            For asymmetric sections, some minor-axis moment may develop. This is because orientation
            of neutral axis is usually not equal to orientation of applied moment vector. As curvature
            increases, some minor-axis moment must develop to maintain equilibrium and to keep the 
            neutral-axis in the same user-specified orientation.
        """
        # use root finding algorithm to find neutral axis depth
        self.axial = P
        phi_list = np.linspace(0, phi_max, num=N_step)
        step=0
        x0=self.depth/2
        
        time_start = time.time()
        for curvature in phi_list:
            step +=1
            root = secant_method(self.verify_equilibrium, args=curvature, x0=0, x1=x0+0.1)
            correct_NA = root
            #root = sp.root_scalar(self.verify_equilibrium, args=curvature, method="secant", x0=0, x1=x0+0.1)
            #correct_NA = root.root
            # if not root.converged:
            #     print("\tstep {}: Could not converge...Ending moment curvature analysis at phi = {}".format(step,curvature))
            #     print(root.flag)
            #     self.curvature.append(curvature)
            #     self.neutral_axis.append(0)
            #     self.momentx.append(0)
            #     self.momenty.append(0)
            #     break
            
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
            
        time_end = time.time()
        self.MK_solved = True
        print("Moment-curvature analysis completed. Elapsed time: {:.2f} seconds\n".format(time_end - time_start))

    
    def verify_equilibrium(self, NA, args):
        """
        Function used for root-finding. 
        Check if equilibrium is established (sumF=0) at assumed neutral axis depth
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
        """retrieve stress-strain data from a node fiber"""
        strain_history = self.node_fibers[tag].strain
        stress_history = [self.node_fibers[tag].stress_strain(x) for x in strain_history]
        force_history = [self.node_fibers[tag].area * x for x in stress_history]
        momentx_history = [self.node_fibers[tag].ecc[1] * x for x in force_history]
        momenty_history = [self.node_fibers[tag].ecc[0] * x for x in force_history]
        
        data_dict={
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
        """retrieve stress-strain data from patch fiber nearest to user-specified coord"""
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
            "fiber_type":self.patch_fibers[tag].name,
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
    
    
    def run_interaction(self, ecu=0.004):
        """
        Start PM interaction analysis.
        
        Algorithm:
            0.) set extreme compression fiber strain to user-specified value
            1.) increment neutral axis depth (c) from 0 to inf
                    at c = 0, pure tension
                    at c = inf, pure compression
            2.) at each c:
                    M = sum(fiber_moment)
                    P = sum(fiber_force)
            3.) back to step 1, assume another c value. Stop when P stops increasing
            4.) repeat step 1-3 with section rotated 180 degrees to get the other side
    
        Please Note:
            Internally within fkit, the sign convention is +P = tension, -P = compression
            This is opposite of what's commonly used within the concrete design industry.
            For plotting and exporting purposes, the sign on P is flipped. 
            But within the backend, the +P = tension convention should be followed
        """
        # increment neutral axis depth from 0 to inf
        NA_depth = list(np.linspace(0.1, self.depth*4, 200))
        P = []
        M = []
        time_start = time.time()
        for c in NA_depth:
            sumF = 0
            sumM = 0
            curvature = ecu / c
            for f in self.patch_fibers:
                F,Mx,My = f.update(curvature, c, solution_found=False)
                sumF += F
                sumM += Mx
            for f in self.node_fibers:
                F,Mx,My = f.update(curvature, c, solution_found=False)
                sumF += F
                sumM += Mx
            # result for T+M is unreliable because strain is too high when c is close to zero
            # only record result
            if sumF < 0: 
                P.append(sumF)
                M.append(sumM)
        
        self.PM_surface[0] = [P,M,NA_depth]
        
        # flip section and repeat
        self.mesh(rotate=180)
        P = []
        M = []
        for c in NA_depth:
            sumF = 0
            sumM = 0
            curvature = ecu / c
            for f in self.patch_fibers:
                F,Mx,My = f.update(curvature, c, solution_found=False)
                sumF += F
                sumM += Mx
            for f in self.node_fibers:
                F,Mx,My = f.update(curvature, c, solution_found=False)
                sumF += F
                sumM += Mx
            if sumF < 0: 
                P.append(sumF)
                M.append(sumM)
        
        self.PM_surface[180] = [P,M,NA_depth]
        
        # restore to original position
        self.mesh(rotate=180) 
        self.PM_solved = True
        time_end = time.time()
        print("PM interaction analysis completed. Elapsed time: {:.2f} seconds\n".format(time_end - time_start))
    
    
    def run_interaction_ACI(self, fpc, fy=60):
        """
        Start PM interaction analysis per ACI-318. Solution is independent
        of user-specified fibers. Input parameter fpc and fy in ksi
        
        Key ACI 318 Assumptions:
            - for concrete, use rectangular stress block (alpha = 0.85, beta ranges from 0.65 to 0.85)
            - for steel, use elastic-perfect-plastic
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
    
        Please Note:
            Internally within fkit, the sign convention is +P = tension, -P = compression
            This is opposite of what's commonly used within the concrete design industry.
            For plotting and exporting purposes, the sign on P is flipped. 
            But within the backend, the +P = tension convention should be followed
        """
        # calculate beta and alpha
        alpha = 0.85
        if fpc < 4:
            beta = 0.85
        elif fpc > 8:
            beta = 0.65
        else:
            beta = 0.85 - 0.05*(fpc*1000-4000)/1000
        
        # increment neutral axis depth from 0 to inf
        NA_depth = list(np.linspace(0.1, self.depth*1.5, 100))
        P = []
        M = []
        phi_list = []
        time_start = time.time()
        for c in NA_depth:
            sumF = 0
            sumM = 0
            greatest_depth = 0
            for f in self.patch_fibers:
                F,Mx,My = f.interaction_ACI(beta*c, alpha*fpc) 
                sumF += F
                sumM += Mx
            for f in self.node_fibers:
                F,Mx,My = f.interaction_ACI(c, fy, fpc) 
                sumF += F
                sumM += Mx
                if f.depth > greatest_depth:
                    greatest_depth = f.depth
            
            # calculate phi factor per ACI
            et = 0.003*(greatest_depth - c)/c
            ey = fy / 29000
            if et>=ey+0.003:
                phi = 0.9
            elif et>=ey and et<ey+0.003:
                phi = 0.75 + 0.15*(et-ey)/((ey+0.003)-ey)
            elif et<ey:
                phi = 0.65
                
            P.append(sumF)
            M.append(sumM)
            phi_list.append(phi)
        self.PM_surface_ACI[0] = [P,M,NA_depth,phi_list]
        
        # flip section and repeat
        self.mesh(rotate=180)
        P = []
        M = []
        phi_list = []
        for c in NA_depth:
            sumF = 0
            sumM = 0
            greatest_depth = 0
            for f in self.patch_fibers:
                F,Mx,My = f.interaction_ACI(beta*c, alpha*fpc) 
                sumF += F
                sumM += Mx
            for f in self.node_fibers:
                F,Mx,My = f.interaction_ACI(c, fy, fpc) 
                sumF += F
                sumM += Mx
                if f.depth > greatest_depth:
                    greatest_depth = f.depth
            
            # calculate phi factor per ACI
            et = 0.003*(greatest_depth - c)/c
            ey = fy / 29000
            if et>=ey+0.003:
                phi = 0.9
            elif et>=ey and et<ey+0.003:
                phi = 0.75 + 0.15*(et-ey)/((ey+0.003)-ey)
            elif et<ey:
                phi = 0.65
                
            P.append(sumF)
            M.append(-sumM)
            phi_list.append(phi)
        self.PM_surface_ACI[180] = [P,M,NA_depth,phi_list]
        
        
        # create factored interaction surface
        Po = min(self.PM_surface_ACI[0][0])
        self.PM_surface_ACI_factored[0] = [[],[],[],[]]
        self.PM_surface_ACI_factored[180] = [[],[],[],[]]
        
        for i in range(len(self.PM_surface_ACI[0][0])):
            if self.PM_surface_ACI[0][0][i] > Po*0.8:
                phi = self.PM_surface_ACI[0][3][i]
                p = self.PM_surface_ACI[0][0][i] * phi
                m = self.PM_surface_ACI[0][1][i] * phi
                c = self.PM_surface_ACI[0][2][i]
                self.PM_surface_ACI_factored[0][0].append(p)
                self.PM_surface_ACI_factored[0][1].append(m)
                self.PM_surface_ACI_factored[0][2].append(c)
                self.PM_surface_ACI_factored[0][3].append(phi)
        
        for i in range(len(self.PM_surface_ACI[180][0])):
            if self.PM_surface_ACI[180][0][i] > Po*0.8:
                phi = self.PM_surface_ACI[180][3][i]
                p = self.PM_surface_ACI[180][0][i] * phi
                m = self.PM_surface_ACI[180][1][i] * phi
                c = self.PM_surface_ACI[180][2][i]
                self.PM_surface_ACI_factored[180][0].append(p)
                self.PM_surface_ACI_factored[180][1].append(m)
                self.PM_surface_ACI_factored[180][2].append(c)
                self.PM_surface_ACI_factored[180][3].append(phi)
        
        # add last point at 0.8Po
        self.PM_surface_ACI_factored[0][0].append(self.PM_surface_ACI_factored[0][0][-1])
        self.PM_surface_ACI_factored[0][1].append(0)
        self.PM_surface_ACI_factored[0][2].append(self.PM_surface_ACI_factored[0][2][-1])
        self.PM_surface_ACI_factored[0][3].append(self.PM_surface_ACI_factored[0][3][-1])
        self.PM_surface_ACI_factored[180][0].append(self.PM_surface_ACI_factored[180][0][-1])
        self.PM_surface_ACI_factored[180][1].append(0)
        self.PM_surface_ACI_factored[180][2].append(self.PM_surface_ACI_factored[180][2][-1])
        self.PM_surface_ACI_factored[180][3].append(self.PM_surface_ACI_factored[180][3][-1])
        
        # restore to original position
        self.mesh(rotate=180) 
        self.PM_solved_ACI = True
        time_end = time.time()
        print("PM interaction analysis per ACI 318 completed. Elapsed time: {:.2f} seconds\n".format(time_end - time_start))
    
    
    
    def create_output_folder(self, result_folder="exported_data_fkit"):
        """Create a folder in current working directory to store results"""
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
        
    
    def export_data(self):
        """
        Export all analysis data to csv
            interaction.csv
            interaction_ACI_nominal.csv
            interaction_ACI_factored.csv
            moment_curvature.csv
        """
        # create folder
        if not self.folder_created:
            self.create_output_folder()
        
        # export data to csv
        if self.MK_solved:
            filename = os.path.join(self.output_dir, "moment_curvature.csv")
            with open(filename,'w') as f:
                f.write("curvature,moment,NA,P,My,slope\n")
                for i in range(len(self.curvature)):
                    f.write(f"{self.curvature[i]},{self.momentx[i]},{self.neutral_axis[i]},{self.axial},{self.momenty[i]},{self.K_tangent[i]}\n")
            
            
        if self.PM_solved_ACI:
            filename = os.path.join(self.output_dir, "interaction_ACI_nominal.csv")
            with open(filename,'w') as f:
                f.write("M,P,NA,orientation\n")
                for i in range(len(self.PM_surface_ACI[0][0])):
                    f.write("{},{},{},0\n".format(
                        self.PM_surface_ACI[0][1][i],
                        -self.PM_surface_ACI[0][0][i],
                        self.PM_surface_ACI[0][2][i]
                        ))
                for i in range(len(self.PM_surface_ACI[180][0])):
                    f.write("{},{},{},180\n".format(
                        self.PM_surface_ACI[180][1][i],
                        -self.PM_surface_ACI[180][0][i],
                        self.PM_surface_ACI[180][2][i]
                        ))
                    
            filename = os.path.join(self.output_dir, "interaction_ACI_factored.csv")
            with open(filename,'w') as f:
                f.write("M,P,NA,phi,orientation\n")
                for i in range(len(self.PM_surface_ACI_factored[0][0])):
                    f.write("{},{},{},{},0\n".format(
                        self.PM_surface_ACI_factored[0][1][i],
                        -self.PM_surface_ACI_factored[0][0][i],
                        self.PM_surface_ACI_factored[0][2][i],
                        self.PM_surface_ACI_factored[0][3][i]
                        ))
                for i in range(len(self.PM_surface_ACI_factored[180][0])):
                    f.write("{},{},{},{},180\n".format(
                        self.PM_surface_ACI_factored[180][1][i],
                        -self.PM_surface_ACI_factored[180][0][i],
                        self.PM_surface_ACI_factored[180][2][i],
                        self.PM_surface_ACI_factored[180][3][i]
                        ))
                
            
        if self.PM_solved:
            filename = os.path.join(self.output_dir, "interaction.csv")
            with open(filename,'w') as f:
                f.write("M,P,NA,orientation\n")
                for i in range(len(self.PM_surface[0][0])):
                    f.write("{},{},{},0\n".format(
                        self.PM_surface[0][1][i],
                        -self.PM_surface[0][0][i],
                        self.PM_surface[0][2][i]
                        ))
                for i in range(len(self.PM_surface[180][0])):
                    f.write("{},{},{},180\n".format(
                        self.PM_surface[180][1][i],
                        -self.PM_surface[180][0][i],
                        self.PM_surface[180][2][i]
                        ))




def secant_method(func,args,x0,x1,TOL=1e-4, max_iteration = 100):
    # edge case for when curvature = 0
    if args == 0:  
        return x0
    
    # start iteration
    for i in range(max_iteration):
        fx0 = func(x0, args)
        fx1 = func(x1, args)
        
        if abs(fx1 - fx0) < TOL:  # converged
            return x1

        try:
            x_next = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
        except ZeroDivisionError:
            print("\tError: Division by zero occurred. The method failed.")
            return None

        x0, x1 = x1, x_next

    print("\tWarning: Maximum number of iterations reached. The method may not have converged.")
    print("\tsumF = {:.2f}".format(func(x1,args)))
    return x1
