def calculate_vegetation_indices(R, G, B, RE=None, NIR=None, L1=1, L2=0.5):
    # 归一化红光指数
    r = R / (R + G + B)
    
    # 归一化绿光指数
    g = G / (R + G + B)
    
    # 归一化蓝光指数
    b = B / (R + G + B)
    
    # 绿蓝比指数GBRI
    GBRI = b / g
    
    # 红绿比指数RGRI
    RGRI = r / g
    
    # 超蓝指数ExB
    ExB = 1.4 * b - g
    
    # 超绿指数ExG
    ExG = 2 * g - r - b
    
    # 超红指数ExR
    ExR = 1.4 * r - g
    
    # 超绿超红差分指数ExGR
    ExGR = ExG - ExR
    
    # 植被颜色提取指数CIVE
    CIVE = 0.441 * r - 0.881 * g + 0.385 * b + 18.78745
    
    # 植被指数VEG 
    # VEG = g / (r**a)*b**(1-a)
    VEG = NIR/(R + G + B)**0.5
    
    # 改进型绿红植被指数MGRVI
    MGRVI = (G**2 - R**2) / (G**2 + R**2)
    
    # 归一化绿红差分指数NGRDI
    NGRDI = (G - R) / (G + R)
    
    # 可见光波段差异植被指数VDVI
    VDVI = (2 * g - r - b) / (2 * g + r + b)
    
    # 综合指数1 COMI
    # COMI = 0.25 * ExG + 0.3 * ExGR + 0.33 * CIVE + 0.12 * VEG
    
    # 综合指数2 COM2
    # COM2 = 0.36 * ExG + 0.47 * CIVE + 0.17 * VEG
    
    # 耐大气植被指数ARVI
    ARVI = (NIR - (2 * R - B)) / (NIR + (2 * R - B))
    
    # 差值植被指数DVI
    DVI = NIR - R
    
    # 增强植被指数EVI
    EVI = 2.5 * (NIR - R) / (NIR + 6 * R - 7.5 * B + L1)
    
    # 绿色归一化差异植被指数GNDVI
    GNDVI = (NIR - G) / (NIR + G)
    
    # 归一化差异红边植被指数NDRE (Only if RE is provided)
    NDRE = (NIR - RE) / (NIR + RE)
    
    # 归一化差异植被指数NDVI
    NDVI = (NIR - R) / (NIR + R)
    
    # 优化的土壤调节植被指数OSAVI
    OSAVI = (NIR - R) / (NIR + R + 0.16)
    
    # 比值植被指数RVI
    RVI = NIR / R
    
    # 土壤调节植被指数SAVI
    # SAVI = ((NIR - R) / (NIR + R + L1)) * (1 + L2)
    
    # 叶面叶绿素指数LCI
    LCI = (NIR - R) / (NIR + R)
    
    return {
        'r': r, 
        'g': g, 
        'b': b, 
        'GBRI': GBRI, 
        'RGRI': RGRI, 
        'ExB': ExB, 
        'ExG': ExG,
        'ExR': ExR, 
        'ExGR': ExGR, 
        'CIVE': CIVE, 
        'MGRVI': MGRVI,
        'NGRDI': NGRDI, 
        'VDVI': VDVI, 
        'ARVI': ARVI,
        'DVI': DVI, 
        'EVI': EVI, 
        'GNDVI': GNDVI, 
        'NDRE': NDRE, 
        'NDVI': NDVI,
        'OSAVI': OSAVI, 
        'RVI': RVI, 
        # 'SAVI': SAVI, 
        'LCI': LCI,
        'VEG':VEG
    }
 