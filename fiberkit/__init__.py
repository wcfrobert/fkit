"""
fkit (fiber kit) is a section analysis program implemented in python. It may be used to perform
moment-curvature, and P+M interaction curve analysis of any cross section of any material type.
"""

__version__ = "2.0.0"
__author__ = "Robert Wang"
__license__ = "MIT"


import fiberkit.nodefiber
import fiberkit.patchfiber
from fiberkit.section import Section
import fiberkit.sectionbuilder
import fiberkit.plotter