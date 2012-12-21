
name=`hostname`


python main.py evolve $1 \
    -p0 "(1.0,1.0,0.6)" \
    -p0-string "('a','edMax','rpoe')" \
    -deltas  "(0.02,0.02,0.01)" \
    -fixedVars "('baryMass','J')" \
    -fixedParams  "[('T',20.0)]" \
    -max-steps 0 \
    -changeBasis False

    # -a1 0. \
    # -a2 1. \
    # -a-steps 2 \
    # -T1 0.  \
    # -T2 30 \
    # -T-steps 2 \
    # -edMin .3 \
    # -edMax 4. \
    # -ed-steps 2 \
    # -rpoe1 1.0 \
    # -rpoe2 0.5 \
    # -rpoe-steps 2 \
    # -RotNS-runtype 3