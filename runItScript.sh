
name=`hostname`

T=30.0
step=0.5
 # python main.py evolve $1 \
 #     -database-file "/home/jeff/work/rotNSruns/tester${T}.step.${step}.db" \
 #     -p0 "(1.0,1.0,0.6)" \
 #     -p0-string "('a','edMax','rpoe')" \
 #     -deltas  "(0.005,0.005,0.0025)" \
 #     -fixedVars "('baryMass','J')" \
 #     -fixedParams  "[('T',$T)]" \
 #     -max-steps 20 \
 #     -changeBasis False 2>&1 | tee  t$T.step.$step.log 


 python main.py runmodels $1\
     -database-file '/home/jeff/work/rotNSruns/cott-ls220-try2.db' \
     -eos-opts "Tabulated(filename= /home/jeff/work/LS220_Tabulated.dat )" \
     -rollMid 14.0 \
     -eos-Tmin 2.0 \
     -a 0.7 \
     -T 28.0 \
     -edMin .1 \
     -edMax 2.0 \
     -ed-steps 40 \
     -rpoe1 1.0 \
     -rpoe2 0.5 \
     -rpoe-steps 2 \
     -RotNS-runtype 3  2>&1  | tee  runmodels2.log 


# Python main.py runmodels $1\
#     -database-file '/home/jeff/work/rotNSruns/mass-shed-models.db' \
#     -a1 0. \
#     -a2 1. \
#     -a-steps 11 \
#     -T1 0.5  \
#     -T2 40  \
#     -T-steps 10 \
#     -edMin .3 \
#     -edMax 4. \
#     -ed-steps 40 \
#     -rpoe1 1.0 \
#     -rpoe2 0.5 \
#     -rpoe-steps 2 \
#     -RotNS-runtype 3  2>&1  | tee  runmodels.log 
