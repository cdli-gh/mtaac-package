from mtaac_package.morph_annotation import morph_converter

m = morph_converter()

examples_lst = [
    ('NF.V.PT', 'NV2=STEM.NV2=STEM'),
    ('NF.V.RDP.PT.TERM', 'NV2=STEM.NV2=STEM.NV2=STEM.N5=TERM'),
    ('NF.V.PT.GEN.TERM', 'NV2=STEM.NV2=STEM.N5=GEN.N5=TERM'),
    ('MID.V.PL.3-SG-S', 'V5=MID.V12=STEM.V12=STEM.V14=3-SG-S'),
]

for case, error in examples_lst:
    print(
        case,
        m.MTAAC2ORACC(case),
        'matches prev. wrong answer:',
        error == m.MTAAC2ORACC(case)[0]
    )
