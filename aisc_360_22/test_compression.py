import aisc_360_22.compression as comp
from math import isclose


def test_member_slenderness():
    L1 = 144.5
    r1 = 2.0

    L2 = 166
    r2 = 1.6
    K2 = 0.8

    assert comp.member_slenderness(L1, r1) == 72.25
    assert comp.member_slenderness(L2, r2, K2) == 83.0


def test_elastic_buckling_stress():
    assert isclose(comp.elastic_buckling_stress(slenderness=68.5), 60.99814111)
    assert isclose(comp.elastic_buckling_stress(slenderness=145), 13.61324745)


def test_ft_elastic_buckling_stress_doubly_symmetric():
    Lcz = 206.3
    Cw = 9940
    Ix=2070
    Iy=92.9
    J=6.03

    assert isclose(comp.ft_elastic_buckling_stress_doubly_symmetric(Lcz, Cw, Ix, Iy, J), 62.1312022)


def test_nominal_flexural_buckling_stress():
    Fy = 50
    assert isclose(comp.nominal_flexural_buckling_stress(Fy, slenderness=68.5), 35.47891211)
    assert isclose(comp.nominal_flexural_buckling_stress(Fy, slenderness=145.0), 11.93881801)


def test_nominal_ft_buckling_stress_doubly_symmetric():
    Fy=50
    Lcz = 206.3
    Cw = 9940
    Ix=2070
    Iy=92.9
    J=6.03

    assert isclose(comp.nominal_ft_buckling_stress_doubly_symmetric(Fy, Lcz, Cw, Ix, Iy, J), 35.70158857)


def test_w_section_capacity():
    # W10X33, Lx=10ft, Ly=10ft, Lz=10ft, Kx=1.0, Ky=1.0, Kz=1.0, Fy=50ksi
    A=9.71
    bf=7.96
    tf=0.435
    d=9.73
    kdes=0.935
    tw=0.290
    Ix=171
    Iy=36.6
    J=0.583
    Cw=791

    Lx=10*12
    Ly=10*12
    Lz=10*12

    kx=1.0
    ky=1.0
    kz=1.0

    Fy=50

    capacity, warnings, notes = comp.w_section_capacity(area=A, Ix=Ix, Iy=Iy, J=J, warping_constant=Cw, 
                                                        flange_width=bf, flange_thickness=tf, section_depth=d, kdes=kdes, web_thickness=tw,
                                                        unbraced_length_x=Lx, unbraced_length_y=Ly, unbraced_length_z=Lz,
                                                        yield_stress=Fy, design_method="ASD", kx=kx, ky=ky, kz=kz,
                                                        x_brace_offset=0, y_brace_offset=0)
    assert isclose(capacity, 220, rel_tol=0.001)
    assert warnings == []
    assert notes == []

    # W10X22, Lx=19.26ft, Ly=5ft, Lz=5ft, Kx=1.0, Ky=1.0, Kz=1.0, Fy=50ksi
    A=6.49
    bf=5.75
    tf=0.360
    d=10.2
    kdes=0.660
    tw=0.240
    Ix=118
    Iy=11.4
    J=0.239
    Cw=275

    Lx=19.26*12
    Ly=5*12
    Lz=5*12

    kx=1.0
    ky=1.0
    kz=1.0

    Fy=50

    capacity, warnings, notes = comp.w_section_capacity(area=A, Ix=Ix, Iy=Iy, J=J, warping_constant=Cw, 
                                                        flange_width=bf, flange_thickness=tf, section_depth=d, kdes=kdes, web_thickness=tw,
                                                        unbraced_length_x=Lx, unbraced_length_y=Ly, unbraced_length_z=Lz,
                                                        yield_stress=Fy, design_method="LRFD", kx=kx, ky=ky, kz=kz,
                                                        x_brace_offset=0, y_brace_offset=0)
    assert isclose(capacity, 236, rel_tol=0.002)
    assert warnings == []
    assert notes == ["Shape is slender for compression."]

    # W10X22, Lx=24ft, Ly=24ft, Lz=24ft, Kx=1.0, Ky=1.0, Kz=1.0, Fy=50ksi
    A=6.49
    bf=5.75
    tf=0.360
    d=10.2
    kdes=0.660
    tw=0.240
    Ix=118
    Iy=11.4
    J=0.239
    Cw=275

    Lx=24*12
    Ly=24*12
    Lz=24*12

    kx=1.0
    ky=1.0
    kz=1.0

    Fy=50

    capacity, warnings, notes = comp.w_section_capacity(area=A, Ix=Ix, Iy=Iy, J=J, warping_constant=Cw, 
                                                        flange_width=bf, flange_thickness=tf, section_depth=d, kdes=kdes, web_thickness=tw,
                                                        unbraced_length_x=Lx, unbraced_length_y=Ly, unbraced_length_z=Lz,
                                                        yield_stress=Fy, design_method="LRFD", kx=kx, ky=ky, kz=kz,
                                                        x_brace_offset=0, y_brace_offset=0)
    assert warnings == ["Slenderness ratio exceeds 200."]
    assert notes == ["Shape is slender for compression."]

    # W14X145, Lx=0ft, Ly varies, Lz=0ft, Kx=1.0, Ky=1.0, Kz=1.0, Fy=50ksi
    A=42.7
    bf=15.5
    tf=1.09
    d=14.8
    kdes=1.69
    tw=0.680
    Ix=1710
    Iy=677
    J=15.2
    Cw=31700

    Lx=0*12
    Lz=0*12

    kx=1.0
    ky=1.0
    kz=1.0

    Fy=50

    strengths = {0:1920,
                  6:1880,
                  7:1860,
                  8:1840,
                  9:1820,
                  10:1800,
                  11:1770,
                  12:1750,
                  13:1720,
                  14:1690,
                  15:1650,
                  16:1620,
                  17:1590,
                  18:1550,
                  19:1510,
                  20:1470,
                  22:1390,
                  24:1310,
                  26:1230,
                  28:1140,
                  30:1060,
                  32:973,
                  34:891,
                  36:812,
                  38:735,
                  40:663}
    
    for length, strength in strengths.items():
        Ly=length*12
        capacity, warnings, notes = comp.w_section_capacity(area=A, Ix=Ix, Iy=Iy, J=J, warping_constant=Cw, 
                                                        flange_width=bf, flange_thickness=tf, section_depth=d, kdes=kdes, web_thickness=tw,
                                                        unbraced_length_x=Lx, unbraced_length_y=Ly, unbraced_length_z=Lz,
                                                        yield_stress=Fy, design_method="LRFD", kx=kx, ky=ky, kz=kz,
                                                        x_brace_offset=0, y_brace_offset=0)
        assert isclose(capacity, strength, rel_tol=0.003)
