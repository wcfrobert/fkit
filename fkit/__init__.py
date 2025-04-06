"""
fkit (fiber kit) is a section analysis program implemented in python. It may be used to perform
moment-curvature, and P+M interaction curve analysis of any cross section of any material type.
"""

__version__ = "1.1.0"
__author__ = "Robert Wang"
__license__ = "MIT"


import fkit.nodefiber
import fkit.patchfiber
from fkit.section import Section
import fkit.sectionbuilder
import fkit.plotter