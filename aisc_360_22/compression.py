"""
Member design per AISC 360-22 Chapter E: "Design of Members for Compression"
"""

from math import pi, sqrt
import pandas as pd
from aisc_360_22.steel_constants import STEEL_ELASTIC_MODULUS, STEEL_SHEAR_MODULUS
import aisc_360_22.design_requirements as dr


"""
Steel design values prescribed in the code
"""
PHI_C = 0.90        # LRFD strength reduction factor for compression
OMEGA_C = 1.67      # ASD safety factor for compression

"""
Table E7.1
"""
EFFECTIVE_WIDTH_ADJUSTMENT_FACTORS = {"a": ("Stiffened elements except walls of suare and rectangular HSS", 0.18, 1.31),
                                      "b": ("Walls of square and rectangular HSS",                          0.20, 1.38),
                                      "c": ("All other elements",                                           0.22, 1.49)}


def member_slenderness(unbraced_length: float, radius_of_gyration: float, effective_length_factor: float=1.0) -> float:
    """
    Calculate member slenderness, Lc/r = KL/r
    If effective length was calculated seperately, enter the effective length as unbraced_length and 
    do not specify an effective length factor.

    unbraced_length = L
    radius_of_gyration = r
    effective_length_factor = K
    """
    return effective_length_factor * unbraced_length / radius_of_gyration


def elastic_buckling_stress(slenderness: float, elastic_modulus: float=STEEL_ELASTIC_MODULUS) -> float:
    """
    Calculate elastic buckling stress per Equation E3-4
    """
    return pi**2 * elastic_modulus / slenderness**2


def ft_elastic_buckling_stress_doubly_symmetric(z_effective_length: float, warping_constant: float, Ix: float, Iy: float, J: float,
                                 elastic_modulus: float=STEEL_ELASTIC_MODULUS, shear_modulus=STEEL_SHEAR_MODULUS) -> float:
    """
    Calculate torsional or flexural-torsional elastic buckling stress per Equation E4-2
    """
    return ( (pi**2 * elastic_modulus * warping_constant) / z_effective_length**2 + shear_modulus*J ) * 1/(Ix + Iy) 


def nominal_flexural_buckling_stress(yield_stress: float, elastic_stress: float=None, slenderness: float=None,
                                     elastic_modulus: float=STEEL_ELASTIC_MODULUS) -> float:
    """
    Calculate flexural buckling stress per Equations E3-2 and E3-3
    Either member slenderness or elastic buckling stress must be specified. 
    If only member slenderness is specified, elastic buckling stress will be determined using Equation E3-4. 
    If elastic buckling stress is specified, member slenderness will be ignored.
    """
    if not elastic_stress:
        elastic_stress = elastic_buckling_stress(slenderness, elastic_modulus)
    if yield_stress/elastic_stress <= 2.25:
        return ( 0.658**(yield_stress/elastic_stress) ) * yield_stress
    else:
        return 0.877 * elastic_stress
    

def nominal_ft_buckling_stress_doubly_symmetric(yield_stress, z_effective_length: float, warping_constant: float, Ix: float, Iy: float, J: float,
                                 elastic_modulus: float=STEEL_ELASTIC_MODULUS, shear_modulus=STEEL_SHEAR_MODULUS) -> float:
    """
    Calculate nominal flexural-torsional stress for a doubly symmetric member per Equation E4-2 
    """
    elastic_stress = ft_elastic_buckling_stress_doubly_symmetric(z_effective_length, warping_constant, Ix, Iy, J, elastic_modulus, shear_modulus)
    buckling_stress = nominal_flexural_buckling_stress(yield_stress, elastic_stress)
    return buckling_stress


def ft_elastic_buckling_stress_i_minor_axis_offset(z_effective_length: float, Iy, J, area, r0, h0, y_offset, 
                                                   elastic_modulus=STEEL_ELASTIC_MODULUS, shear_modulus=STEEL_SHEAR_MODULUS):
    """
    Equation E4-10
    """
    return (pi**2*elastic_modulus*Iy/z_effective_length**2*(h0**2/4+y_offset**2)+shear_modulus*J) * 1/(area*r0**2)


def ft_elastic_buckling_stress_i_major_axis_offset(z_effective_length, Ix, Iy, J, area, r0, h0, x_offset,
                                                   elastic_modulus=STEEL_ELASTIC_MODULUS, shear_modulus=STEEL_SHEAR_MODULUS):
    """
    Equation E4-12
    """
    return (pi**2*elastic_modulus*Iy/z_effective_length**2 * (h0**2/4+Ix/Iy*x_offset**2)+shear_modulus*J) * 1/(area*r0**2)


def calc_r0(rx, ry, xa, ya):
    """
    Use Equation E4-11 to calculate r0 for use in Equations 4-10 and 4-12
    """
    return rx**2+ry**2+xa**2+ya**2


def nominal_ft_buckling_stress_i_bracing_offset(yield_stress, z_effective_length, Ix, Iy, J, area, r0, h0, x_offset, y_offset,
                                                elastic_modulus=STEEL_ELASTIC_MODULUS, shear_modulus=STEEL_SHEAR_MODULUS):
    """
    Nominal flexural-torsional buckling stress
    """
    x_elastic_stress = ft_elastic_buckling_stress_i_major_axis_offset(z_effective_length, Ix, Iy, J, area, r0, h0, x_offset,
                                                                      elastic_modulus, shear_modulus)
    y_elastic_stress = ft_elastic_buckling_stress_i_minor_axis_offset(z_effective_length, Iy, J, area, r0, h0, y_offset,
                                                                      elastic_modulus, shear_modulus)
    elastic_stress = min(x_elastic_stress, y_elastic_stress)
    buckling_stress = nominal_flexural_buckling_stress(yield_stress, elastic_stress)
    return buckling_stress


def elastic_local_buckling_stress(c2: float, wt_ratio: float, limiting_wt_ratio: float, yield_stress: float) -> float:
    """
    Elastic local buckling stress per Equation E7-5
    """
    return (c2*limiting_wt_ratio/wt_ratio)**2 * yield_stress


def effective_width(nominal_width, wt_ratio, limiting_wt_ratio, yield_stress, nominal_stress, elastic_local_stress, c1) -> float:
    """
    Effective width for slender elements (excluding round HSS) per Equations E7-2 and E7-3.
    """
    if wt_ratio <= limiting_wt_ratio*sqrt(yield_stress/nominal_stress):
        return nominal_width
    else:
        return nominal_width * (1-c1*sqrt(elastic_local_stress/nominal_stress)) * sqrt(elastic_local_stress/nominal_stress)
    

def w_section_effective_area(gross_area, flange_width, flange_thickness,
                             section_depth, kdes, web_thickness, 
                             yield_stress, nominal_stress) -> float:
    """
    Calculate the effective area of a W section
    """
    flange_wt_ratio = flange_width / (2*flange_thickness)
    web_height = section_depth - 2*kdes
    web_wt_ratio = web_height / web_thickness
    flange_c1 = EFFECTIVE_WIDTH_ADJUSTMENT_FACTORS["c"][1]
    flange_c2 = EFFECTIVE_WIDTH_ADJUSTMENT_FACTORS["c"][2]
    flange_limiting_wt_ratio = dr.limiting_wt_ratio_comp(table_case=1, elastic_modulus=STEEL_ELASTIC_MODULUS,
                                                    yield_strength=yield_stress)
    flange_elastic_local_buckling_stress = elastic_local_buckling_stress(flange_c2, flange_wt_ratio, flange_limiting_wt_ratio, yield_stress)
    effective_flange_width = effective_width(flange_width, flange_wt_ratio, flange_limiting_wt_ratio, 
                                             yield_stress, nominal_stress, flange_elastic_local_buckling_stress, flange_c1)
    
    web_c1 = EFFECTIVE_WIDTH_ADJUSTMENT_FACTORS["a"][1]
    web_c2 = EFFECTIVE_WIDTH_ADJUSTMENT_FACTORS["a"][2]
    web_limiting_wt_ratio = dr.limiting_wt_ratio_comp(table_case=5, elastic_modulus=STEEL_ELASTIC_MODULUS, yield_strength=yield_stress)
    web_elastic_local_buckling_stress = elastic_local_buckling_stress(web_c2, web_wt_ratio, web_limiting_wt_ratio, yield_stress)
    effective_web_height = effective_width(web_height, web_wt_ratio, web_limiting_wt_ratio, 
                                           yield_stress, nominal_stress, web_elastic_local_buckling_stress, web_c1)
    if dr.is_slender_comp(flange_wt_ratio, flange_limiting_wt_ratio) or dr.is_slender_comp(web_wt_ratio, web_limiting_wt_ratio):
        effective_area = gross_area - 2*flange_thickness*(flange_width-effective_flange_width) - web_thickness*(web_height-effective_web_height)
    else:
        effective_area = gross_area
    return effective_area


def w_section_capacity(area, Ix, Iy, J, warping_constant, flange_width, flange_thickness, section_depth, kdes, web_thickness,
                       unbraced_length_x, unbraced_length_y, unbraced_length_z,
                       yield_stress, design_method="nominal",
                       elastic_modulus=STEEL_ELASTIC_MODULUS, shear_modulus=STEEL_SHEAR_MODULUS,
                       kx=1.0, ky=1.0, kz=1.0,
                       x_brace_offset=0.0, y_brace_offset=0.0, return_report=False):
    """
    Calculate the compression capacity of a W column using all applicable limit states
    Returns nominal capacity unless LRFD or ASD is specified
    """
    # Make zero lengths nonzero to avoid division by zero errors
    if unbraced_length_x == 0:
        unbraced_length_x = 0.00001
    if unbraced_length_y == 0:
        unbraced_length_y = 0.00001
    if unbraced_length_z == 0:
        unbraced_length_z = 0.00001
    warnings = []
    notes = []
    report = {}
    rx = sqrt(Ix/area)
    ry = sqrt(Iy/area)
    r0 = calc_r0(rx, ry, x_brace_offset, y_brace_offset)
    h0 = section_depth - flange_thickness
    slenderness_x = member_slenderness(unbraced_length_x, rx, kx)
    slenderness_y = member_slenderness(unbraced_length_y, ry, ky)
    design_slenderness = max(slenderness_x, slenderness_y)
    report.update({"Governing slenderness ratio, Lc/r": [design_slenderness, ""]})
    if design_slenderness > 200:
        warnings.append("Slenderness ratio exceeds 200.")
    effective_length_z = unbraced_length_z*kz
    flexural_buckling_stress = nominal_flexural_buckling_stress(yield_stress=yield_stress, slenderness=design_slenderness,
                                                                elastic_modulus=elastic_modulus)
    report.update({"Nominal flexural buckling stress (Eqns E3-2, E3-3)": [flexural_buckling_stress, "stress"]})
    if x_brace_offset or y_brace_offset:
        torsional_buckling_stress = nominal_ft_buckling_stress_i_bracing_offset(yield_stress, effective_length_z, Ix, Iy, J, area,
                                                                                r0, h0, x_brace_offset, y_brace_offset, 
                                                                                elastic_modulus, shear_modulus)
        report.update({"Nominal torsional buckling stress (Eqn E4-2)": [torsional_buckling_stress, "stress"]})
    else:
        torsional_buckling_stress = nominal_ft_buckling_stress_doubly_symmetric(yield_stress=yield_stress, z_effective_length=effective_length_z,
                                                                            warping_constant=warping_constant, Ix=Ix, Iy=Iy, J=J, 
                                                                            elastic_modulus=elastic_modulus, shear_modulus=shear_modulus)
        report.update({"Nominal torsional buckling stress (Eqns E4-10, E4-12)": [torsional_buckling_stress, "stress"]})    
    if x_brace_offset and y_brace_offset:
        warnings.append("Torsional buckling results not valid with bracing offset in both axes.")
    
    nominal_stress = min(flexural_buckling_stress, torsional_buckling_stress)
    report.update({"Governing nominal buckling stress, Fn": [nominal_stress, "stress"]})
    effective_area = w_section_effective_area(gross_area=area, flange_width=flange_width, flange_thickness=flange_thickness,
                                              section_depth=section_depth, kdes=kdes, web_thickness=web_thickness, 
                                              yield_stress=yield_stress, nominal_stress=nominal_stress)
    report.update({"Effective area accounting for slender elements, Ae (Sect. E7)": [effective_area, "area"]})
    slender = dr.w_is_slender_comp(flange_width, flange_thickness, section_depth, kdes, web_thickness, yield_stress, elastic_modulus)
    if slender:
        notes.append("Shape is slender for compression.")
    nominal_compressive_strength = nominal_stress * effective_area
    report.update({"Nominal compressive strength, Pn (Eqns E3-1, E4-1, E7-1)": [nominal_compressive_strength, "force"]})

    match design_method:
        case "nominal":
            if return_report:
                return report, warnings, notes
            else:
                return nominal_compressive_strength, warnings, notes
        case "LRFD":
            factored_strength = PHI_C * nominal_compressive_strength
            report.update({"Resistance factor, φ": [PHI_C, ""], "Factored compressive strength, φPn": [factored_strength, "force"]})
            if return_report:
                return report, warnings, notes
            else:
                return factored_strength, warnings, notes
        case "ASD":
            allowable_strength = nominal_compressive_strength / OMEGA_C
            report.update({"Safety factor, Ω": [OMEGA_C, ""], "Allowable compressive strength, Pn/Ω": [allowable_strength, "force"]})
            if return_report:
                return report, warnings, notes
            else:
                return allowable_strength, warnings, notes
        case _:
            raise ValueError("Design method must be \'nominal\', \'LRFD\', or \'ASD\'.")


def w_section_capacity_from_series(section: pd.Series, unbraced_length_x, unbraced_length_y, unbraced_length_z,
                       yield_stress, design_method="nominal",
                       elastic_modulus=STEEL_ELASTIC_MODULUS, shear_modulus=STEEL_SHEAR_MODULUS,
                       kx=1.0, ky=1.0, kz=1.0,
                       x_brace_offset=0.0, y_brace_offset=0.0, value_only=False, return_report=False) -> float:
    area=section.loc["A"]
    Ix=section.loc["Ix"]
    Iy=section.loc["Iy"]
    J=section.loc["J"]
    warping_constant=section.loc["Cw"]
    flange_width=section.loc["bf"]
    flange_thickness=section.loc["tf"]
    section_depth=section.loc["d"]
    kdes=section.loc["kdes"]
    web_thickness=section.loc["tw"]
    capacity, warnings, notes = w_section_capacity(area, Ix, Iy, J, warping_constant, flange_width, flange_thickness, section_depth, kdes, web_thickness, 
                              unbraced_length_x, unbraced_length_y, unbraced_length_z, yield_stress,
                              design_method, elastic_modulus, shear_modulus, kx, ky, kz, x_brace_offset, y_brace_offset, return_report=return_report)
    if value_only:
        return capacity
    else:
        return capacity, warnings, notes