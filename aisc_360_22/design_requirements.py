"""
AISC 360-22 Chapter B: "Design Requirements"
"""

from math import sqrt


def is_slender_comp(wt_ratio: float, limiting_wt_ratio: float) -> bool:
    """
    Determine if member is slender for axial compression per Table B4.1a
    """
    if wt_ratio > limiting_wt_ratio:
        return True
    else:
        return False


def w_is_slender_comp(flange_width, flange_thickness, section_depth, kdes, web_thickness, yield_stress, elastic_modulus):
    """
    Determine if a W section is slender for axial compression
    """
    flange_wt_ratio = flange_width / (2*flange_thickness)
    web_height = section_depth - kdes
    web_wt_ratio = web_height / web_thickness

    flange_limiting_wt_ratio = limiting_wt_ratio_comp(1, elastic_modulus, yield_stress)
    web_limiting_wt_ratio = limiting_wt_ratio_comp(5, elastic_modulus, yield_stress)

    if flange_wt_ratio > flange_limiting_wt_ratio or web_wt_ratio > web_limiting_wt_ratio:
        return True
    else:
        return False


def limiting_wt_ratio_comp(table_case: int, elastic_modulus: float, yield_strength: float, kc: float=None) -> float:
    """
    Limiting width-to-thickness ratios per Table B4.1a
    """
    match table_case:
        case 1:
            return 0.56*sqrt(elastic_modulus/yield_strength)
        case 2:
            return 0.64*sqrt(kc*elastic_modulus/yield_strength)
        case 3:
            return 0.45*sqrt(elastic_modulus/yield_strength)
        case 4:
            return 0.75*sqrt(elastic_modulus/yield_strength)
        case 5:
            return 1.49*sqrt(elastic_modulus/yield_strength)
        case 6:
            return 1.40*sqrt(elastic_modulus/yield_strength)
        case 7:
            return 0.40*sqrt(elastic_modulus/yield_strength)
        case 8:
            return 1.49*sqrt(elastic_modulus/yield_strength)
        case 9:
            return 0.11*elastic_modulus/yield_strength
        case _:
            raise ValueError("Table case must be integer between 1 and 9.")
