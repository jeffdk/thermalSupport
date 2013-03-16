
name=`hostname`
cd ~/thermalSupport/
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
     -database-file '/home/jeff/work/rotNSruns/newHS.db' \
     -eosPrescription      "{'type': 'tableFromEosDriver',
      'sc.orgTableFile': '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5',
      'prescriptionName': 'isothermal',
      'ye': 0.12,
      'rollMid': 14.0,
      'rollScale': 0.5,
      'eosTmin': 0.01}" \
     -a 0.5 \
     -T 20.0 \
     -edMin .1 \
     -edMax 3.0 \
     -ed-steps 20 \
     -rpoe1 1.0 \
     -rpoe2 0.5 \
     -rpoe-steps 2 \
     -RotNS-runtype 3  2>&1  | tee  newHS.log


# Python main.py runmodels $1\
#     -database-file '/home/jeff/work/rotNSruns/mass-shed-models.db' \

#step=1

# python main.py evolve $1 \
#      -database-file "/home/jeff/work/rotNSruns/jan14b.${T}.s${step}.cb.db" \
#      -p0 "(1.0,0.9,0.75)" \
#      -p0-string "('a','edMax','rpoe')" \
#      -deltas  "(0.02,0.02,0.01)" \
#      -fixedVars "('baryMass','J')" \
#      -fixedParams  "[('T',$T)]" \
#      -max-steps 75 
#      -changeBasis True 2>&1 | tee  jan14b.${T}.s${step}.cb.log 

#    -eos-opts   "Tabulated(filename=/home/jeff/work/HS_Tabulated.dat)" \
#    -eos-opts "Gamma(Gamma=2;Kappa=122.)" \

# python main.py runmodels $1\
#     -eos-opts   "Tabulated(filename=/home/jeff/work/LS220_Tabulated.dat)" \
#     -database-file "/home/jeff/work/rotNSruns/ls-TOV-new.db" \
#     -a 0.0  \
#     -T 0.5 \
#     -edMin 0.1 \
#     -edMax 6.0 \
#     -ed-steps 96 \
#     -rpoe 1.0 \
#     -RotNS-runtype 30  2>&1  | tee  ls-tov-new-cold.log 



# python main.py runmodels $1\
#     -eos-opts "Gamma(Gamma=2;Kappa=122.)" \
#     -database-file "/home/jeff/work/rotNSruns/spec-gam2-tov.db" \
#     -eos-Tmin 0.0 \
#     -a 0.0  \
#     -T 0.0 \
#     -edMin .1 \
#     -edMax 6.0 \
#     -ed-steps 72 \
#     -rpoe 1.0 \
#     -RotNS-runtype 30  2>&1  | tee  spec-gam2-tov.log 

# python main.py runmodels $1\
#     -eos-opts   'Tabulated(filename= /home/jeff/work/LS220_Tabulated.dat )' \
#     -database-file '/home/jeff/work/rotNSruns/ls-TEST.db' \
#     -a1 0. \
#     -a2 1. \
#     -a-steps 11 \
#     -T 0.5  \
#     -edMin .3 \
#     -edMax 4. \
#     -ed-steps 40 \
#     -rpoe1 1.0 \
#     -rpoe2 0.5 \
#     -rpoe-steps 2 \
#     -RotNS-runtype 3  2>&1  | tee  ls-TEST.log 

# python main.py runmodels $1\
#     -database-file '/home/jeff/work/rotNSruns/dontCare.db' \
#     -a 1.0 \
#     -T 20.0  \
#     -ed .75 \
#     -rpoe 0.66 -RotNS-runtype 30  2>&1  | tee  single-sekiguchi.log 
