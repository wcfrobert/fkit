"""
Point fiber material models.

Patch fibers have vertices and occupy some area geometrically. Mostly used for concrete.
Node fibers are defined by their centroid (a single point). Mostly used for rebar.

Currently available:
    1. Bilinear
    2. Multilinear
    3. RambergOsgood
    4. MenegottoPinto
    5. Custom_Trilinear
"""

class BaseNodeFiber:
    """
    Parent Node fiber:
        coord               coordinate of node fiber [x,y]
        
        area                fiber area
        
        default_color       original color for visualization
        
        ecc                 distance from fiber to section centroid [dx,dy]
        
        depth               distance from max(y) of section to fiber
        
        tag                 unique ID tag for the fiber
        
        strain              strain progression (+tensile, -compressive)
        
        stress              stress progression (+tensile, -compressive)
        
        force               force contribution progression. F = stress * area
        
        moment              moment contribution progression, M = force * ecc
        
        color_list          fiber color progression. Based on stress state for visualization
    
    Compressive strain/stress is negative (-)
    Tensile strain/stress is positive (+)
    """
    def __init__(self, coord, area, default_color):
        self.coord = coord if coord != None else [0,0]
        self.name = "BaseFiberClass"
        self.area = area if area != None else 1.0
        self.default_color = default_color
        self.ecc = None
        self.depth = None
        self.tag = None
        
        self.strain = []
        # commented out to reduce memory consumption, can be derived from strain
        #self.stress = []
        #self.force = []
        #self.momentx = []
        #self.momenty = []
        self.color_list = []
        
    def update_location(self, section_centroid, section_ymax):
        """update fiber location with respect to section centroid"""
        self.depth = section_ymax - self.coord[1] 
        self.ecc = [self.coord[0] - section_centroid[0], section_centroid[1] - self.coord[1]]
    
    def update(self, curvature, NA_depth, solution_found=False):
        """as curvature increases, store fiber states"""       
        if solution_found:
            strain = curvature*(-NA_depth + self.depth)
            stress = self.stress_strain(strain)
            force = stress * self.area
            momentx = force * self.ecc[1]
            momenty = force * self.ecc[0]
            color_current = self.color_map(strain, stress)
            self.strain.append(strain)
            #self.stress.append(stress)
            #self.force.append(force)
            #self.momentx.append(momentx)
            #self.momenty.append(momenty)
            self.color_list.append(color_current)
            return force, momentx, momenty
        else:
            strain = curvature*(-NA_depth + self.depth)
            stress = self.stress_strain(strain)
            force = stress * self.area
            momentx = force * self.ecc[1]
            momenty = force * self.ecc[0]
            return force, momentx, momenty
    
    def interaction_ACI(self, c, fy, fpc, Es):
        """used for finding interaction surface per ACI 318 assumptions"""
        strain = 0.003*(self.depth - c)/c
        if strain > 0:
            # tension
            stress = strain * Es
            if stress > fy:
                stress = fy
            force = stress * self.area
            momentx = force * self.ecc[1]
            momenty = force * self.ecc[0]
            return force, momentx, momenty
        else:
            # compression
            stress = strain * Es
            if stress < -fy:
                stress = -fy
            force = (stress + 0.85*fpc) * self.area #add 0.85fpc because stress is -ve
            momentx = force * self.ecc[1]
            momenty = force * self.ecc[0]
            return force, momentx, momenty
    
    #abstractmethod
    def stress_strain(self, strain):
        """
        OVERRIDE - define material stress-strain relationship
        """
        print("WARNING: fiber stress-strain relationship not defined")
        return 0
    
    #abstractmethod
    def color_map(self):
        """
        OVERRIDE - define color map for fiber for visualization purposes
        """
        print("WARNING: fiber color map not defined")
        return self.default_color








class Bilinear(BaseNodeFiber):
    """
    Simple bilinear model for steel.
        
    Input parameters: (ALL POSITIVE)
        fy              steel yield stress
        
        Es              elastic modulus
        
        fu              (OPTIONAL)steel ultimate stress
                            - Default = fy
        
        ey              (OPTIONAL) yield strain
                            - Default = fy / Es
                            
        emax            (OPTIONAL) maximum strain, after which stress = 0
                            - Default = 0.1
                            - (ref A) suggests 0.16 for rebar, 0.3 for mild steel
                            
        default_color   (OPTIONAL) color of patch for visualization purposes
                            - Default = "slategray"
                            
    Stress-Strain Relationship:
        Behavior is same in compression and tension and is defined by two straight lines and three points:
            first linear portion: (0,0) up to (ey, fy) with slope of Es
            second linear portion: (ey, fy) to (emax, fu)
            after emax, stress becomes zero (fracture).
        
        If strain < ey:
            stress = Es * strain
        If strain > ey:
            stress = fy + (fu - fy)/(emax-ey) * (strain - ey)
        If strain > emax:
            stress = 0
            
    References:
        A. Rex & Easterling (1996). Behavior and Modeling of Mild and Reinforcing Steel.
    """
    def __init__(self, fy, Es, fu="default", ey="default", emax=0.1, 
                 default_color="black", coord=None, area=None):
        super().__init__(coord, area, default_color=default_color)
        self.name = "Bilinear"
        self.fy = fy
        self.fu = fy if fu=="default" else fu
        self.Es = Es
        self.ey = fy/Es if ey=="default" else ey
        self.emax = emax
        
    def stress_strain(self, strain):
        """monotonic stress-strain relationship"""
        stress = self.Es * strain
        
        if stress < -self.fy:
            stress = -self.fy + (self.fu-self.fy)/(self.emax-self.ey) *(strain + self.ey)
        elif stress > self.fy:
            stress = self.fy + (self.fu-self.fy)/(self.emax-self.ey) *(strain - self.ey)
        
        if self.emax != "inf" and (strain < -self.emax or strain > self.emax):
            stress = 0
            
        return stress
        
    def color_map(self, strain, stress):
        """color map for visualization"""
        if abs(strain) > self.emax:
               return "white"  
        else:
            # blue to red color map (Paul Bourke - Colour Ramping for Data Visualization)
            # matplotlib cmap is really slow
            lerp_color = [1.0, 1.0, 1.0]
            dv = 1
            if stress<-self.fy:
                stress = -self.fy
            elif stress>self.fy:
                stress = self.fy
            v = 1-(stress + self.fy) / (self.fy*2)
            
            if v < 0.25*dv:
                lerp_color[0] = 0
                lerp_color[1] = 4*v/dv
            elif v < 0.5*dv:
                lerp_color[0] = 0
                lerp_color[2] = 1 + 4*(0.25*dv-v)/dv
            elif v < 0.75*dv:
                lerp_color[0] = 4*(v-0.5*dv)/dv
                lerp_color[2] = 0
            else:
                lerp_color[1] = 1 + 4*(0.75*dv-v)/dv
                lerp_color[2] = 0
            
            return lerp_color




class Multilinear(BaseNodeFiber):
    """
    Multilinear model for steel. Based on Rex & Easterling (1996). 
    Six distinct regions that traces out the recognizable steel stress-strain curve
        
    Input parameters: (ALL POSITIVE)
        fy              steel yield stress
        
        fu              steel ultimate stress
        
        Es              elastic modulus
                            
        ey1             (OPTIONAL) strain at beginning of yield plateau
                            - Default = fy/Es
        ey2             (OPTIONAL) strain at end of yield plateau
                            - (ref A) recommends 0.008 for rebar, 0.02 for mild steel
        strain1         (OPTIONAL) strain end of 3rd line
                            - (ref A) recommends 0.03 for rebar, 0.05 for mild steel
        strain2         (OPTIONAL) strain at end 4th line
                            - (ref A) recommends 0.07 for rebar, 0.10 for mild steel                    
        strain3         (OPTIONAL) strain at end of 5th line (strain at peak stress)
                            - (ref A) recommends 0.10 for rebar, 0.20 for mild steel                        
        strain4         (OPTIONAL) strain at end of 6th line
                            - (ref A) recommends 0.16 for rebar, 0.30 for mild steel
                            - This is also equal to the maximum strain (emax)                     
                            
        stress1         (OPTIONAL) stress end of 3rd line (%Fu)
                            - (ref A) recommends 0.85 for rebar, 0.83 for mild steel
        stress2         (OPTIONAL) stress at end 4th line (%Fu)
                            - (ref A) recommends 0.98 for rebar, 0.95 for mild steel
        stress3         (OPTIONAL) stress at end of 5th line (%Fu) (peak stress)
                            - Default = 1.0
        stress4         (OPTIONAL) stress at end of 6th line (%Fu)
                            - (ref A) recommends 0.84 for rebar, 0.83 for mild steel
                            
        default_color   (OPTIONAL) color of node for visualization purposes
                            - Default = "black"
                            
    Stress-Strain Relationship:
        Behavior is same in compression and tension and is defined by six straight lines.
        Curve traces out the very recognizable steel stress-strain curve. See (ref A) for details

        If strain < ey1:
            stress = Es * strain
        If between [ey1,ey2]
            stress = fy
        if between [ey2,strain1]
            stress = fy + (stress1-fy)/(strain1-ey2) * (strain-ey2)
        if between [strain1, strain2]
            stress = stress1 + (stress2-stress1)/(strain2-strain1) * (strain-strain1)
        if between [strain2, strain3]
            stress = stress2 + (stress3-stress2)/(strain3-strain2) * (strain-strain2)
        if between [strain3, strain4]
            stress = stress3 + (stress4-stress3)/(strain4-strain3) * (strain-strain3)
        if above strain4
            stress = 0
            
    References:
        A. Rex & Easterling (1996). Behavior and Modeling of Mild and Reinforcing Steel.
    """
    def __init__(self, fy, fu, Es, ey1="default", ey2=0.008,
                 stress1=0.83, stress2=0.98, stress3=1.00, stress4=0.84, 
                 strain1=0.03, strain2=0.07, strain3=0.10, strain4=0.16, 
                 default_color="black", coord=None, area=None):
        super().__init__(coord, area, default_color=default_color)
        self.name = "Multilinear"
        self.fy = fy
        self.fu = fu
        self.Es = Es
        self.ey1 = fy/Es if ey1=="default" else ey1
        self.ey2 = ey2
        self.emax = strain4
        
        self.strain1 = strain1
        self.strain2 = strain2
        self.strain3 = strain3
        self.strain4 = strain4
        
        self.stress1 = stress1 * fu
        self.stress2 = stress2 * fu
        self.stress3 = stress3 * fu
        self.stress4 = stress4 * fu
        
    def stress_strain(self, strain):
        """monotonic stress-strain relationship"""
        is_positive = True if strain>0 else False
        strain = abs(strain)
        
        if strain <= self.ey1:
            stress = self.Es * strain
        elif strain > self.ey1 and strain <= self.ey2:
            stress = self.fy
        elif strain > self.ey2 and strain <= self.strain1:
            stress = self.fy + (self.stress1-self.fy)/(self.strain1-self.ey2) * (strain-self.ey2)
        elif strain > self.strain1 and strain <= self.strain2:
            stress = self.stress1 + (self.stress2-self.stress1)/(self.strain2-self.strain1) * (strain-self.strain1)
        elif strain > self.strain2 and strain <= self.strain3:
            stress = self.stress2 + (self.stress3-self.stress2)/(self.strain3-self.strain2) * (strain-self.strain2)
        elif strain > self.strain3 and strain <= self.strain4:
            stress = self.stress3 + (self.stress4-self.stress3)/(self.strain4-self.strain3) * (strain-self.strain3)
        elif strain > self.strain4:
            stress = 0
        
        if is_positive:
            return stress
        else:
            return -stress
        
    def color_map(self, strain, stress):
        """color map for visualization"""
        if abs(strain) > self.emax:
               return "white"  
        else:
            # blue to red color map (Paul Bourke - Colour Ramping for Data Visualization)
            # matplotlib cmap is really slow
            lerp_color = [1.0, 1.0, 1.0]
            dv = 1
            if stress<-self.fu:
                stress = -self.fu
            elif stress>self.fu:
                stress = self.fu
            v = 1-(stress + self.fu) / (self.fu*2)
            
            if v < 0.25*dv:
                lerp_color[0] = 0
                lerp_color[1] = 4*v/dv
            elif v < 0.5*dv:
                lerp_color[0] = 0
                lerp_color[2] = 1 + 4*(0.25*dv-v)/dv
            elif v < 0.75*dv:
                lerp_color[0] = 4*(v-0.5*dv)/dv
                lerp_color[2] = 0
            else:
                lerp_color[1] = 1 + 4*(0.75*dv-v)/dv
                lerp_color[2] = 0
            
            return lerp_color




class RambergOsgood(BaseNodeFiber):
    """
    A smooth power function for steel fiber. Ramberg-Osgood formulation.
        
    Input parameters: (ALL POSITIVE)
        fy              steel yield stress
        
        Es              elastic modulus
                            
        n               RambergOsgood parameter
                            - Lower value = smoother curve
                            - Adjust as needed to fit your data
                            
        emax            (OPTIONAL) maximum strain, after which stress = 0
                            - Default = 0.16
                            - (ref C) suggests 0.16 for rebar, 0.3 for mild steel
                            
        default_color   (OPTIONAL) color of node for visualization purposes
                            - Default = "black"
                            
    Stress-Strain Relationship:
        Stress-strain behavior is modeled by a smooth power function.
        Here we are using the alternative form with 0.2% offset.
            strain = stress/E + 0.002 (stress/fy)^n
            
        Use Newton-Raphson iterate and solve for stress
            derivative = 1/E + (0.002/fy)(n) * (stress/fy)^(n-1)
            
    References:
        A. Bruneau, Uang, Sabelli (2011). Ductile Design of Steel Structures 2nd ed.
        B. https://mechanicalc.com/reference/mechanical-properties-of-materials#note-strain-hardening-exponent
        C. Rex & Easterling (1996). Behavior and Modeling of Mild and Reinforcing Steel.
    """
    def __init__(self, fy, Es, n, emax=0.16, 
                 default_color="black", coord=None, area=None):
        super().__init__(coord, area, default_color=default_color)
        self.name = "RambergOsgood"
        self.fy = fy
        self.Es = Es
        self.n = n
        self.emax = emax
        
    def stress_strain(self, strain):
        """monotonic stress-strain relationship"""
        is_positive = True if strain>0 else False
        strain = abs(strain)
        
        # Newton raphson (x = sigma, fx = strain)
        tol = 1e-5 #tolerance of 0.00001
        x0 = 0 #initial guess
        N = 0 #terminate if cannot converge
        func = 999
        x = x0
        while abs(func) > tol:
            N = N + 1
            func = x/self.Es + 0.002 * (x/self.fy)**(self.n) - strain
            func_prime = 1/self.Es + (0.002/self.fy) * (self.n) * (x/self.fy)**(self.n - 1)
            x = x - func/func_prime
            if N > 999:
                raise RuntimeError("Newton Raphson could not converge")
        stress = x
        
        # check if limiting strain is exceeded
        if strain > self.emax:
            stress = 0
            
        if is_positive:
            return stress
        else:
            return -stress
        
    def color_map(self, strain, stress):
        """color map for visualization"""
        if abs(strain) > self.emax:
               return "white"  
        else:
            # blue to red color map (Paul Bourke - Colour Ramping for Data Visualization)
            # matplotlib cmap is really slow
            lerp_color = [1.0, 1.0, 1.0]
            dv = 1
            if stress<-self.fy:
                stress = -self.fy
            elif stress>self.fy:
                stress = self.fy
            v = 1-(stress + self.fy) / (self.fy*2)
            
            if v < 0.25*dv:
                lerp_color[0] = 0
                lerp_color[1] = 4*v/dv
            elif v < 0.5*dv:
                lerp_color[0] = 0
                lerp_color[2] = 1 + 4*(0.25*dv-v)/dv
            elif v < 0.75*dv:
                lerp_color[0] = 4*(v-0.5*dv)/dv
                lerp_color[2] = 0
            else:
                lerp_color[1] = 1 + 4*(0.75*dv-v)/dv
                lerp_color[2] = 0
            
            return lerp_color





class MenegottoPinto(BaseNodeFiber):
    """
    A smooth power function for steel fiber. Menegotto-Pinto formulation.
        
    Input parameters: (ALL POSITIVE)
        fy              steel yield stress
        
        Es              elastic modulus
                            
        b               Menegotto Pinto parameter
                            - Adjusts strain hardening slope
                            - Adjust as needed to fit your data
                            
        n               Menegotto Pinto parameter
                            - Lower value = smoother curve
                            - Adjust as needed to fit your data
                            
        emax            (OPTIONAL) maximum strain, after which stress = 0
                            - Default = 0.16
                            - (ref B) suggests 0.16 for rebar, 0.3 for mild steel
                            
        default_color   (OPTIONAL) color of node for visualization purposes
                            - Default = "black"
                            
    Stress-Strain Relationship:
        Stress-strain behavior is modeled by a smooth power function. May be more robust
        than Ramberg-Osgood as no Newton Raphson iteration is needed.
            stress = (  b*eo + (1-b)*eo/ (1 + eo^n)^(1/n) ) * fy
            where:
                eo = strain / ey
                b = ratio of final to initial tangent stiffness
                n = menegotto-pinto parameter
            
    References:
        A. Bruneau, Uang, Sabelli (2011). Ductile Design of Steel Structures 2nd ed.
        B. Rex & Easterling (1996). Behavior and Modeling of Mild and Reinforcing Steel.
    """
    def __init__(self, fy, Es, b, n, emax=0.16, 
                 default_color="black", coord=None, area=None):
        super().__init__(coord, area, default_color=default_color)
        self.name = "MenegottoPinto"
        self.fy = fy
        self.Es = Es
        self.b = b
        self.n = n
        self.emax = emax
        
    def stress_strain(self, strain):
        """monotonic stress-strain relationship"""
        is_positive = True if strain>0 else False
        strain = abs(strain)
        
        # calculate stress
        ey = self.fy / self.Es
        eo = strain / ey
        stress = (  self.b*eo + (1-self.b)*eo/ (1 + eo**self.n)**(1/self.n) ) * self.fy
        
        # check if limiting strain is exceeded
        if strain > self.emax:
            stress = 0
            
        if is_positive:
            return stress
        else:
            return -stress
        
    def color_map(self, strain, stress):
        """color map for visualization"""
        if abs(strain) > self.emax:
               return "white"  
        else:
            # blue to red color map (Paul Bourke - Colour Ramping for Data Visualization)
            # matplotlib cmap is really slow
            lerp_color = [1.0, 1.0, 1.0]
            dv = 1
            if stress<-self.fy:
                stress = -self.fy
            elif stress>self.fy:
                stress = self.fy
            v = 1-(stress + self.fy) / (self.fy*2)
            
            if v < 0.25*dv:
                lerp_color[0] = 0
                lerp_color[1] = 4*v/dv
            elif v < 0.5*dv:
                lerp_color[0] = 0
                lerp_color[2] = 1 + 4*(0.25*dv-v)/dv
            elif v < 0.75*dv:
                lerp_color[0] = 4*(v-0.5*dv)/dv
                lerp_color[2] = 0
            else:
                lerp_color[1] = 1 + 4*(0.75*dv-v)/dv
                lerp_color[2] = 0
            
            return lerp_color



class Custom_Trilinear(BaseNodeFiber):
    """
    A custom trilinear stress-strain relationship defined by three points. 
    Can be asymmetric.
        
    Input parameters: (POSITVE FOR TENSION, NEGATIVE FOR COMPRESSION)
        stress1p         stress at point 1 (tension)
        stress2p         stress at point 2 (tension)
        stress3p         stress at point 3 (tension)
        strain1p         strain at point 1 (tension)
        strain2p         strain at point 2 (tension)
        strain3p         strain at point 3 (tension)
                            - Maximum strain emax; stress = 0 beyond
                            - (ref A) suggests 0.16 for rebar, 0.3 for mild steel
        
        stress1n         (OPTIONAL) stress at point 1 (compression)
                            - Default = same as positive values
        stress2n         (OPTIONAL) stress at point 2 (compression)
                            - Default = same as positive values
        stress3n         (OPTIONAL) stress at point 3 (compression)
                            - Default = same as positive values
        strain1n         (OPTIONAL) strain at point 1 (compression)
                            - Default = same as positive values
        strain2n         (OPTIONAL) strain at point 2 (compression)
                            - Default = same as positive values
        strain3n         (OPTIONAL) strain at point 3 (compression)
                            - Default = same as positive values
                            
        default_color   (OPTIONAL) color of node for visualization purposes
                            - Default = "black"
                            
    Stress-Strain Relationship:
        Stress-strain behavior is modeled by three straight lines. Can be asymmetrically defined.
            
    References:
        A. Rex & Easterling (1996). Behavior and Modeling of Mild and Reinforcing Steel.
    """
    def __init__(self, strain1p, strain2p, strain3p, stress1p, stress2p, stress3p,
                 strain1n="default", strain2n="default", strain3n="default",
                 stress1n="default", stress2n="default", stress3n="default",
                 default_color="black", coord=None, area=None):
        super().__init__(coord, area, default_color=default_color)
        self.name = "Custom Trilinear"
        self.strain1p = strain1p
        self.strain2p = strain2p
        self.strain3p = strain3p
        self.stress1p = stress1p
        self.stress2p = stress2p
        self.stress3p = stress3p
        
        self.strain1n = -strain1p if strain1n=="default" else strain1n
        self.strain2n = -strain2p if strain2n=="default" else strain2n
        self.strain3n = -strain3p if strain3n=="default" else strain3n
        self.stress1n = -stress1p if stress1n=="default" else stress1n
        self.stress2n = -stress2p if stress2n=="default" else stress2n
        self.stress3n = -stress3p if stress3n=="default" else stress3n
        
    def stress_strain(self, strain):
        """monotonic stress-strain relationship"""
        if strain < 0:
            # compression backbone curve
            if strain >= self.strain1n:
                stress = 0 + (self.stress1n - 0)/(self.strain1n - 0) * strain
            elif strain >= self.strain2n:
                stress = self.stress1n + (self.stress2n - self.stress1n)/(self.strain2n - self.strain1n) * (strain - self.strain1n)
            elif strain >= self.strain3n:
                stress = self.stress2n + (self.stress3n - self.stress2n)/(self.strain3n - self.strain2n) * (strain - self.strain2n)
            elif strain < self.strain3n:
                stress = 0
        else:
            # tension backbone curve
            if strain <= self.strain1p:
                stress = 0 + (self.stress1p - 0)/(self.strain1p - 0) * strain
            elif strain <= self.strain2p:
                stress = self.stress1p + (self.stress2p - self.stress1p)/(self.strain2p - self.strain1p) * (strain - self.strain1p)
            elif strain <= self.strain3p:
                stress = self.stress2p + (self.stress3p - self.stress2p)/(self.strain3p - self.strain2p) * (strain - self.strain2p)
            elif strain > self.strain3p:
                stress = 0
            
        return stress
        
    def color_map(self, strain, stress):
        """color map for visualization"""
        if strain < 0:
            if stress <= self.stress1p:
                return "lightcoral"
            elif stress <= self.stress2p:
                return "indianred"
            elif stress <= self.stress3p:
                return "brown"
            elif stress > self.stress3p:
                return "white"
        else:
            if stress <= self.stress1p:
                return "lightsteelblue"
            elif stress <= self.stress2p:
                return "cornflowerblue"
            elif stress <= self.stress3p:
                return "royalblue"
            elif stress > self.stress3p:
                return "white"
