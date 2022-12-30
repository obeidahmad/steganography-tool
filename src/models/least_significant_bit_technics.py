from enum import Enum


class LSBTechnics(str, Enum):
    INLINE = "inline"
    EQUI_DISTRIBUTION = "equi_distribution"
    MIDPOINT_CIRCLE = "midpoint_circle"