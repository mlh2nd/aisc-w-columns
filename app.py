import streamlit as st
import pandas as pd
import sections_db as sd
import aisc_360_22.compression as comp

section_data = sd.aisc_w_sections()

st.title("AISC W-Section Column Designer")

st.write("This webapp calculates the compression capacity of standard wide-flange columns using ANSI/AISC 360-22, \
         _Specification for Structural Steel Buildings_. \
         It checks flexural buckling, torsional buckling, and slender elements. \
         The results have been checked for agreement with several configurations in Tables 4-1 and 6-1 of \
         the AISC _Steel Construction Manual_, with no differences exceeding 1\%.")
st.write("Enter design parameters in the sidebar (on a mobile device, press the \">\" in the upper left corner to expand the sidebar). \
         Use the tabs below to see detailed design results for a single section or to see all sections that meet the design criteria.")
st.write("Referenced equations are from Chapter E of the _Specification_. \
         For more details, download the free PDF from the AISC website: https://www.aisc.org/Specification-for-Structural-Steel-Buildings-ANSIAISC-360-22-Download")
st.write("This webapp is provided for convenience only. All results must be verified by a qualified engineer before use \
         in real-world structural design.")
st.write("If any errors or bugs are encountered, please raise an issue on Github: https://github.com/mlh2nd/aisc-w-columns/issues")

with st.sidebar:
    st.header("Design Parameters")
    applied_load = st.number_input("Applied axial compression (kips)", min_value=0.0, step=0.01)
    cola, colb = st.columns(2)
    with cola:
        yield_stress = st.number_input("Steel yield stress (ksi)", min_value=0, value=50)
    with colb:
        design_method = st.selectbox("Design method", ["LRFD", "ASD", "nominal"])
    st.write("Unbraced lengths and effective length factors:")
    colc, cold = st.columns(2)
    with colc:
        length_x = st.number_input("Lx", min_value=0.0, step=0.01) * 12
        length_y = st.number_input("Ly", min_value=0.0, step=0.01) * 12
        length_z = st.number_input("Lz", min_value=0.0, step=0.01) * 12
    with cold:
        length_factor_x = st.number_input("Kx", min_value=0.0, step=0.01, value=1.0)
        length_factor_y = st.number_input("Ky", min_value=0.0, step=0.01, value=1.0)
        length_factor_z = st.number_input("Kz", min_value=0.0, step=0.01, value=1.0)
    st.write("Lx = unbraced length for major-axis buckling.")
    st.write("Ly = unbraced length for minor-axis buckling.")
    st.write("Lz = unbraced length for torsional buckling.")

tab1, tab2 = st.tabs(["Check single section", "See all adequate sections sorted by weight"])

with tab1:
    st.header("Summary")
    col1, col2 = st.columns(2)
    with col1:
        section_name = st.selectbox("Section", section_data.index)
        section = section_data.loc[section_name]
        capacity, warnings, notes = comp.w_section_capacity_from_series(section, length_x, length_y, length_z, yield_stress, design_method, 
                                               kx=length_factor_x, ky=length_factor_y, kz=length_factor_z)
        st.write(f"Section Capacity: {round(capacity, 1)} kips")
        stress_ratio = applied_load/capacity
        st.write(f"Utilization Ratio: {round(stress_ratio, 2)}")
        if stress_ratio <= 1.0:
            st.write("DESIGN CHECK: OK")
        else:
            st.write("DESIGN CHECK: NO GOOD")
    with col2:
        st.write("#### Warnings:")
        if warnings:
            for warning in warnings:
                st.write(warning)
        else:
            st.write("No warnings")
        st.write("#### Notes:")
        if notes:
            for note in notes:
                st.write(note)
        else:
            st.write("No notes")
    st.header("Section Data")
    st.table(pd.DataFrame(section).transpose().style.format({"W":"{:.1f}", "A":"{:.2f}", "d":"{:.2f}", "bf":"{:.2f}",
                                                             "tw":"{:.3f}", "tf":"{:.3f}", "kdes":"{:.3f}",
                                                             "Ix":"{:.2f}", "Zx":"{:.2f}", "Sx":"{:.2f}", "rx":"{:.3f}",
                                                             "Iy":"{:.2f}", "Zy":"{:.2f}", "Sy":"{:.2f}", "ry":"{:.3f}",
                                                             "J":"{:.4f}", "Cw":"{:.2f}", "T":"{:.2f}"}))
    st.image("Diagram.png")
    st.write("Diagram created in LibreCAD")
    st.header("Design Details")
    report = comp.w_section_capacity_from_series(section, length_x, length_y, length_z, yield_stress, design_method, 
                                               kx=length_factor_x, ky=length_factor_y, kz=length_factor_z, value_only=True, return_report=True)
    units = {"":"", "force":"kip", "stress": "ksi", "area": "in²"}
    for description, value in report.items():
        st.write(description + " = " + str(round(value[0], 2)) + " " + units[value[1]])
with tab2:
    col3, col4 = st.columns(2)
    with col3:
        dmax = st.number_input("Maximum depth", min_value=0.0, value=16.0)
        dmin = st.number_input("Minimum depth", min_value=0.0)
    with col4:
        bmax = st.number_input("Maximum width", min_value=0.0, value=16.0)
        bmin = st.number_input("Minimum width", min_value=0.0)
    filtered_sections = section_data.copy()
    capacities = filtered_sections.apply(comp.w_section_capacity_from_series,axis=1, 
                                         unbraced_length_x=length_x, unbraced_length_y=length_y, unbraced_length_z=length_z,
                                         yield_stress=yield_stress, design_method=design_method, 
                                         kx=length_factor_x, ky=length_factor_y, kz=length_factor_z, value_only=True)
    stress_ratios = capacities.apply(lambda x: applied_load/x)
    filtered_sections = filtered_sections.filter(["W", "d", "bf", "tw", "tf"])
    filtered_sections.insert(1, "Capacity", capacities)
    filtered_sections.insert(2, "SR", stress_ratios)
    filtered_sections = sd.sort_by_weight(filtered_sections)
    section_mask = filtered_sections["Capacity"] >= applied_load
    filtered_sections = filtered_sections.loc[section_mask]
    filtered_sections = sd.sections_filter(sd.sections_filter(filtered_sections, "le", d=dmax), "ge", d=dmin)
    filtered_sections = sd.sections_filter(sd.sections_filter(filtered_sections, "le", bf=bmax), "ge", bf=bmin)
    st.table(filtered_sections.style.format({"W":"{:.1f}", "d":"{:.2f}", "bf":"{:.2f}", "tw":"{:.3f}", "tf":"{:.3f}",
                                             "Capacity":"{:.2f}", "SR":"{:.2f}"}))