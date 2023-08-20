"""
Patch fiber material model. 

Patch fibers have vertices and occupy some area geometrically. Mostly used for concrete.
Node fibers are defined by their centroid (a single point). Mostly used for rebar.

Currently available:
    1. Hognestad
    2. Mander
    3. Todeschini
    4. Bilinear
    5. Multilinear
    6. RambergOsgood
    7. MenegottoPinto
    8. Custom_Trilinear
"""
import math

class BasePatchFiber:
    """
    Parent patch fiber:
        vertices            list of [x,y] coordinates of the fiber's vertices [[],[],...]
                                - First and last coordinate must overlap (i.e. [xo,yo] = [xn,yn])
                                - Vertices must be consecutive and ordered counter-clockwise along perimeter.
                                
        default_color       original patch color for visualization
        
        ecc                 distance from fiber centroid to section centroid [dx,dy]
        
        depth               distance from max(y) of section to fiber centroid
        
        area                fiber area
        
        centroid            centroid of fiber [x_c,y_c]
        
        tag                 unique ID tag for the fiber
        
        strain              strain progression (+tensile, -compressive)
        
        stress              stress progression (+tensile, -compressive)
        
        force               force contribution progression. F = stress * area
        
        moment              moment contribution progression, M = force * ecc
        
        color_list          fiber color progression. Based on stress state for visualization
    
    Compressive strain/stress is negative (-)
    Tensile strain/stress is positive (+)
    """
    def __init__(self, vertices, default_color):
        self.vertices = vertices if vertices != None else [[0,0],[1,0],[1,1],[0,1],[0,0]]
        self.name = "BaseFiberClass"
        self.default_color = default_color
        self.ecc = None
        self.depth = None
        self.area = None
        self.centroid = None
        self.tag = None
        
        self.strain = []
        # commented out to reduce memory consumption, can be derived from strain
        #self.stress = []
        #self.force = []
        #self.momentx = []
        #self.momenty = []
        self.color_list = []
    
    def find_geometric_properties(self):
        """find centroid of fiber"""
        # shoelace formula
        x_list = [a[0] for a in self.vertices]
        y_list = [a[1] for a in self.vertices]
        products = []
        for i in range(len(x_list)-1):
            products.append(x_list[i]*y_list[i+1] - x_list[i+1]*y_list[i])
        self.area = 0.5 * sum(products)
        
        # centroid of polygon
        cx_product = []
        cy_product = []
        for i in range(len(x_list)-1):
            cx_product.append( (x_list[i]+x_list[i+1]) * (x_list[i]*y_list[i+1] - x_list[i+1]*y_list[i]) )
            cy_product.append( (y_list[i]+y_list[i+1]) * (x_list[i]*y_list[i+1] - x_list[i+1]*y_list[i]) )
        x_c = 1/6/self.area * sum(cx_product)
        y_c = 1/6/self.area * sum(cy_product)
        self.centroid = [x_c, y_c]
        
    def update_location(self, section_centroid, section_ymax):
        """update fiber location with respect to section centroid"""
        self.depth = section_ymax - self.centroid[1] 
        self.ecc = [self.centroid[0] - section_centroid[0], section_centroid[1] - self.centroid[1]]
    
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
    
    def interaction_ACI(self, beta_c, alpha_fpc):
        """used for finding interaction surface per ACI 318 assumptions"""
        if self.depth > beta_c:
            stress = 0
        else:
            stress = -alpha_fpc
        force = stress * self.area
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
    

    
class Hognestad(BasePatchFiber):
    """
    Modified Hognestad model based on Hognestad et al (1951). See Macgregor & Wight Textbook Ch 3.5
        
    Input parameters: (ALL POSITIVE)
        fpc             concrete cylinder strength
                            - Peak stress will occur at 0.9fpc
                            - (ref A) 10% reduction accounts for difference between cylinder strength and member strength 
                            
        Ec              (OPTIONAL) modulus of elasticity
                            - Automatically calculated if not specified. Unit is inferred:
                            - If fpc < 15 (unit ksi): Default = 57000 * sqrt(fpc*1000)/1000
                            - If fpc > 15 (unit MPa): Default = 4700 * sqrt(fpc)
                            
        eo              (OPTIONAL) strain at peak stress
                            - Default = 1.8(fo)/Ec
                            - Expression from is (ref A). Calculated value typically around 0.002
                            - For confined concrete, (ref B) provides equations. Ranges from 0.002 to 0.01
                            
        emax            (OPTIONAL) max strain
                            - Default = 0.0038
                            - (ref A) uses 0.0038 which is appropriate for plain unconfined concrete
                            - For confined concrete, (ref B) provides equations. Ranges from 0.004 to 0.04.
                            
        alpha           (OPTIONAL) stress after max strain as a percentage of fpc
                            - Default = 0
                            - If alpha = 0, fiber becomes inactive and stress = 0 after emax
                            
                            
        take_tension    (OPTIONAL) boolean to consider concrete in tension
                            - Default = False
                            - If take_tension = False, stress will always be zero in tension
                            
        fr              (OPTIONAL) modulus of rupture
                            - Automatically calculated if not specified. Unit is inferred:
                            - If fpc < 15 (unit ksi): Default = 7.5 * sqrt(fpc*1000) / 1000
                            - If fpc > 15 (unit MPa): Default = 0.62 * sqrt(fpc)
                            
        er              (OPTIONAL) strain at modulus of rupture
                            - Default = 0.00015 
                            - (ref A) ranges from 0.00014 to 0.0002
                            
        default_color   (OPTIONAL) color of patch for visualization purposes
                            - Default = "lightgray"
                            
    Stress-Strain Relationship:
        Compression:
        1. parabolic stage up to peak (eo < strain)
                fo = -0.9fpc
                eo = -1.8(fo)/Ec            
                X = strain/eo
                stress = (fo)(2X - X^2)
        2. linear descending stage (emax < strain < eo)
                stress = (fo) + (0.15*fo)/(emax - eo) * (eo-strain)
        3. constant beyond maximum strain (strain < emax)
                stress = -(alpha)fo
          
        Tension:
        1. if take_tension is False
                stress = 0
        2. if take_tension is True, linear with slope of Ec up to (er,fr), then zero
                if strain > er:
                    stress = 0
                else:
                    stress = Ec * strain
                    
    References:
        A. Wight & MacGregor (2012). Reinforced Concrete Mechanics & Design 6E.
        B. Moehle (2014). Seismic Design of Reinforced Concrete Buildings
    """
    def __init__(self, fpc, Ec="default", eo="default", emax=0.0038, alpha=0, 
                 take_tension=False, fr="default", er="default",
                 default_color="lightgray", vertices=None):
        
        super().__init__(vertices, default_color=default_color)
        self.name = "Hognestad"
        self.fpc = fpc
        self.alpha = alpha
        
        is_imperial_unit = True if fpc <= 15 else False
        if is_imperial_unit:
            self.Ec = 57000*math.sqrt(fpc*1000)/1000 if Ec=="default" else Ec
            self.fr = 7.5*math.sqrt(fpc)/1000 if fr=="default" else fr
        else:  # SI unit
            self.Ec = 4700*math.sqrt(fpc) if Ec=="default" else Ec
            self.fr = 0.62*math.sqrt(fpc) if fr=="default" else fr
        
        self.eo = -1.8*0.9*fpc/self.Ec if eo=="default" else -eo
        self.emax = -0.0038 if emax=="default" else -emax
        self.fo = -0.9*fpc
        
        self.take_tension = take_tension
        self.er = 0.00015 if er=="default" else er
    
    def stress_strain(self, strain):
        """monotonic stress-strain relationship"""
        if strain >= 0:
            # tension
            if self.take_tension:
                if self.er < strain:
                    stress = 0
                else:
                    stress = self.Ec * strain
            else:
                stress = 0
        else:
            # compression
            if strain >= self.eo:
                X = strain/self.eo
                stress = self.fo * (2*X-X*X) 
            elif strain >= self.emax:
                stress = self.fo + ((0.15)*self.fo)/(self.emax-self.eo) * (self.eo-strain)
            else:
                stress = self.alpha*self.fo
        
        return stress
    
    
    def color_map(self, strain, stress):
        """color map for visualization"""
        # if in tension
        if strain > 0 and self.take_tension:
            if strain > self.er:
                return self.default_color
            else:
                return "skyblue"
        elif strain > 0:
            return self.default_color
            
        
        # if beyond max strain
        if strain < self.emax:
            return "white"
        else:
            # blue to red color map (Paul Bourke - Colour Ramping for Data Visualization)
            # matplotlib cmap is really slow
            lerp_color = [1.0, 1.0, 1.0]
            dv = 1
            v = abs(stress / self.fo)
            
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



class Mander(BasePatchFiber):
    """
    Mander model based on Mander et al (1988). See Moehle Textbook Ch 4.4.3
        
    Input parameters: (ALL POSITIVE)
        fpc             concrete strength (peak stress)
        
        eo              strain at peak stress
                            - For confined concrete, (ref B) provides equations. Ranges from 0.002 to 0.01
                            
        emax            max strain
                            - (ref A) uses 0.0038 which is appropriate for plain unconfined concrete
                            - For confined concrete, (ref B) provides equations. Ranges from 0.004 to 0.04.
                            
        Ec              (OPTIONAL) modulus of elasticity
                            - Automatically calculated if not specified. Unit is inferred:
                            - If fpc < 15 (unit ksi): Default = 57000 * sqrt(fpc*1000)/1000
                            - If fpc > 15 (unit MPa): Default = 4700 * sqrt(fpc)
                            
        eo              strain at peak stress
                            - For confined concrete, (ref B) provides equations. Ranges from 0.002 to 0.01
                            
        emax            max strain
                            - (ref A) uses 0.0038 which is appropriate for plain unconfined concrete
                            - For confined concrete, (ref B) provides equations. Ranges from 0.004 to 0.04.
                            
        alpha           (OPTIONAL) stress after max strain as a percentage of fpc
                            - Default = 0
                            - If alpha = 0, fiber becomes inactive and stress = 0 after emax
                            
                            
        take_tension    (OPTIONAL) boolean to consider concrete in tension
                            - Default = False
                            - If take_tension = False, stress will always be zero in tension
                            
        fr              (OPTIONAL) modulus of rupture
                            - Automatically calculated if not specified. Unit is inferred:
                            - If fpc < 15 (unit ksi): Default = 7.5 * sqrt(fpc*1000) / 1000
                            - If fpc > 15 (unit MPa): Default = 0.62 * sqrt(fpc)
                            
        er              (OPTIONAL) strain at modulus of rupture
                            - Default = 0.00015 
                            - (ref A) ranges from 0.00014 to 0.0002
                            
        default_color   (OPTIONAL) color of patch for visualization purposes
                            - Default = "lightgray"
                            
    Stress-Strain Relationship:
        Compression:
        1. Unlike the Hognestad model, Mander model is based on a single expression
                fo = -1.0fpc       
                X = strain/eo
                r = Ec / (Ec - fo/eo)
                stress = (fo)(X)(r) / (r - 1 + X^r)
        2. constant beyond maximums train (strain < emax)
                stress = -(alpha)fo
          
        Tension:
        1. if take_tension is False
                stress = 0
        2. if take_tension is True, linear with slope of Ec up to (er,fr), then zero
                if strain > er:
                    stress = 0
                else:
                    stress = Ec * strain
                    
    References:
        A. Wight & MacGregor (2012). Reinforced Concrete Mechanics & Design 6E.
        B. Moehle (2014). Seismic Design of Reinforced Concrete Buildings
    """
    def __init__(self, fpc, eo, emax, Ec="default", alpha=0, 
                 take_tension=False, fr="default", er="default",
                 default_color="lightgray", vertices=None):
        
        super().__init__(vertices, default_color=default_color)
        self.name = "Mander"
        self.fpc = fpc
        self.alpha = alpha
        
        is_imperial_unit = True if fpc <= 15 else False
        if is_imperial_unit:
            self.Ec = 57000*math.sqrt(fpc*1000)/1000 if Ec=="default" else Ec
            self.fr = 7.5*math.sqrt(fpc)/1000 if fr=="default" else fr
        else:  # SI unit
            self.Ec = 4700*math.sqrt(fpc) if Ec=="default" else Ec
            self.fr = 0.62*math.sqrt(fpc) if fr=="default" else fr
            
        self.eo = -eo
        self.emax = -emax
        self.fo = -1.0*fpc
        
        self.take_tension = take_tension
        self.er = 0.00015 if er=="default" else er
    
    def stress_strain(self, strain):
        """monotonic stress-strain relationship"""
        if strain >= 0:
            # tension
            if self.take_tension:
                if self.er < strain:
                    stress = 0
                else:
                    stress = self.Ec * strain
            else:
                stress = 0
        else:
            # compression
            if self.emax < strain:
                X = strain/self.eo
                r = self.Ec / (self.Ec - self.fo/self.eo)
                stress = (self.fo)*(X)*(r) / (r - 1 + X**r)
            else:
                stress = self.alpha*self.fo
        
        return stress
    
    
    def color_map(self, strain, stress):   
        """color map for visualization"""
        # if in tension
        if strain > 0 and self.take_tension:
            if strain > self.er:
                return self.default_color
            else:
                return "skyblue"
        elif strain > 0:
            return self.default_color
        
        # if beyond max strain
        if strain < self.emax:
            return "white"
        else:
            # blue to red color map (Paul Bourke - Colour Ramping for Data Visualization)
            # matplotlib cmap is really slow
            lerp_color = [1.0, 1.0, 1.0]
            dv = 1
            v = abs(stress / self.fo)
            
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





class Todeschini(BasePatchFiber):
    """
    Mander model based on Todeschini et al (1964). See Macgregor & Wight Textbook Ch 3.5
        
    Input parameters: (ALL POSITIVE)
        fpc             concrete cylinder strength
                            - Peak stress will occur at 0.9fpc
                            - (ref A) 10% reduction accounts for difference between cylinder strength and member strength 
                            
        Ec              (OPTIONAL) modulus of elasticity
                            - Automatically calculated if not specified. Unit is inferred:
                            - If fpc < 15 (unit ksi): Default = 57000 * sqrt(fpc*1000)/1000
                            - If fpc > 15 (unit MPa): Default = 4700 * sqrt(fpc)
                            
        eo              (OPTIONAL) strain at peak stress
                            - Default = 1.71(fo)/Ec
                            - Expression from is (ref A). Calculated value typically around 0.002
                            - For confined concrete, (ref B) provides equations. Ranges from 0.002 to 0.01
                            
        emax            (OPTIONAL) max strain
                            - Default = 0.0038
                            - (ref A) uses 0.0038 which is appropriate for plain unconfined concrete
                            - For confined concrete, (ref B) provides equations. Ranges from 0.004 to 0.04.
                            
        alpha           (OPTIONAL) stress after max strain as a percentage of fpc
                            - Default = 0
                            - If alpha = 0, fiber becomes inactive and stress = 0 after emax
                            
                            
        take_tension    (OPTIONAL) boolean to consider concrete in tension
                            - Default = False
                            - If take_tension = False, stress will always be zero in tension
                            
        fr              (OPTIONAL) modulus of rupture
                            - Automatically calculated if not specified. Unit is inferred:
                            - If fpc < 15 (unit ksi): Default = 7.5 * sqrt(fpc*1000) / 1000
                            - If fpc > 15 (unit MPa): Default = 0.62 * sqrt(fpc)
                            
        er              (OPTIONAL) strain at modulus of rupture
                            - Default = 0.00015 
                            - (ref A) ranges from 0.00014 to 0.0002
                            
        default_color   (OPTIONAL) color of patch for visualization purposes
                            - Default = "lightgray"
                            
    Stress-Strain Relationship:
        Compression:
        1. Unlike the Hognestad model, Todeschini model is based on a single expression
                fo = 0.9fpc       
                X = strain/eo
                stress = 2(fo)(X) / (1 + X^2)
        2. constant beyond maximums train (strain < emax)
                stress = -(alpha)fo
          
        Tension:
        1. if take_tension is False
                stress = 0
        2. if take_tension is True, linear with slope of Ec up to (er,fr), then zero
                if strain > er:
                    stress = 0
                else:
                    stress = Ec * strain
                    
    References:
        A. Wight & MacGregor (2012). Reinforced Concrete Mechanics & Design 6E.
        B. Moehle (2014). Seismic Design of Reinforced Concrete Buildings
    """
    def __init__(self, fpc, Ec="default", eo="default", emax=0.0038, alpha=0, 
                 take_tension=False, fr="default", er="default",
                 default_color="lightgray", vertices=None):
        
        super().__init__(vertices, default_color=default_color)
        self.name = "Todeschini"
        self.fpc = fpc
        self.alpha = alpha
        
        is_imperial_unit = True if fpc <= 15 else False
        if is_imperial_unit:
            self.Ec = 57000*math.sqrt(fpc*1000)/1000 if Ec=="default" else Ec
            self.fr = 7.5*math.sqrt(fpc)/1000 if fr=="default" else fr
        else:  # SI unit
            self.Ec = 4700*math.sqrt(fpc) if Ec=="default" else Ec
            self.fr = 0.62*math.sqrt(fpc) if fr=="default" else fr
            
        self.eo = -1.71*0.9*fpc/self.Ec if eo=="default" else -eo
        self.emax = -0.0038 if emax=="default" else -emax
        self.fo = -0.9*fpc
        
        self.take_tension = take_tension
        self.er = 0.00015 if er=="default" else er
    
    def stress_strain(self, strain):
        """monotonic stress-strain relationship"""
        if strain >= 0:
            # tension
            if self.take_tension:
                if self.er < strain:
                    stress = 0
                else:
                    stress = self.Ec * strain
            else:
                stress = 0
        else:
            # compression
            if self.emax < strain:
                X = strain/self.eo
                stress = 2*(self.fo)*(X) / (1 + X**2)
            else:
                stress = self.alpha*self.fo
        
        return stress
    
    def color_map(self, strain, stress):
        """color map for visualization"""
        # if in tension
        if strain > 0 and self.take_tension:
            if strain > self.er:
                return self.default_color
            else:
                return "skyblue"
        elif strain > 0:
            return self.default_color
        
        # if beyond max strain
        if strain < self.emax:
            return "white"
        else:
            # blue to red color map (Paul Bourke - Colour Ramping for Data Visualization)
            # matplotlib cmap is really slow
            lerp_color = [1.0, 1.0, 1.0]
            dv = 1
            v = abs(stress / self.fo)
            
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






class Bilinear(BasePatchFiber):
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
    def __init__(self, fy, Es, fu="default", ey="default", emax=0.1, default_color="slategray", vertices=None):
        super().__init__(vertices, default_color=default_color)
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



class Multilinear(BasePatchFiber):
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
                            
        default_color   (OPTIONAL) color of patch for visualization purposes
                            - Default = "slategray"
                            
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
                 default_color="slategray", vertices=None):
        super().__init__(vertices, default_color=default_color)
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




class RambergOsgood(BasePatchFiber):
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
                            
        default_color   (OPTIONAL) color of patch for visualization purposes
                            - Default = "slategray"
                            
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
    def __init__(self, fy, Es, n, emax=0.16, default_color="slategray", vertices=None):
        super().__init__(vertices, default_color=default_color)
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





class MenegottoPinto(BasePatchFiber):
    """
    A smooth power function for steel fiber. Menegotto-Pinto formulation.
        
    Input parameters: (ALL POSITIVE)
        fy              steel yield stress
        
        Es              elastic modulus
                            
        b               Menegotto Pinto parameter
                            - Adjusts strain hardening slope
                            - Adjust as needed to fit your data.
                            
        n               Menegotto Pinto parameter
                            - Lower value = smoother curve
                            - Adjust as needed to fit your data.
                            
        emax            (OPTIONAL) maximum strain, after which stress = 0
                            - Default = 0.16
                            - (ref B) suggests 0.16 for rebar, 0.3 for mild steel
                            
        default_color   (OPTIONAL) color of patch for visualization purposes
                            - Default = "slategray"
                            
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
    def __init__(self, fy, Es, b, n, emax=0.16, default_color="slategray", vertices=None):
        super().__init__(vertices, default_color=default_color)
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



class Custom_Trilinear(BasePatchFiber):
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
                            
        default_color   (OPTIONAL) color of patch for visualization purposes
                            - Default = "slategray"
                            
    Stress-Strain Relationship:
        Stress-strain behavior is modeled by three straight lines. Can be asymmetrically defined.
            
    References:
        A. Rex & Easterling (1996). Behavior and Modeling of Mild and Reinforcing Steel.
    """
    def __init__(self, strain1p, strain2p, strain3p, stress1p, stress2p, stress3p,
                 strain1n="default", strain2n="default", strain3n="default",
                 stress1n="default", stress2n="default", stress3n="default",
                 default_color="slategray", vertices=None):
        super().__init__(vertices, default_color=default_color)
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

