import os

scale_vars = [
    (0.5, 0.5, 0.0),
    (0.5, 1.0, 1.0),
    (0.5, 2.0, 2.0),
    (1.0, 0.5, 3.0),
    (1.0, 2.0, 5.0),
    (2.0, 0.5, 6.0),
    (2.0, 1.0, 7.0),
    (2.0, 2.0, 8.0),

]


#txt = """weight : Alt$(LHEScaleWeight[{idx}],1)
#alt-norm : Alt$(LHEScaleSumw[{idx}],1)
#"""
txt = """weight : LHEScaleWeight[{idx}]
alt-norm : LHEScaleSumw[{idx}]
"""
filename_template = "fr-muR_{mur}_muF_{muf}.txt"
for scalevar in scale_vars:
    mur, muf, scaleindex = scalevar
    murstr = str(mur).replace(".", "p")
    mufstr = str(muf).replace(".", "p")
    f = open(filename_template.format(mur = murstr, muf = mufstr), "w")
    f.write(txt.format(idx = int(scaleindex)))
    f.close()
