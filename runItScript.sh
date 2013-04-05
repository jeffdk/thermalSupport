
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
     -database-file '/home/jeff/work/rotNSruns/newHS.db' \
     -eosPrescription      "{'type': 'tableFromEosDriver',
      'sc.orgTableFile': '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5',
      'prescriptionName': 'isothermal',
      'ye': 0.12,
      'rollMid': 14.0,
      'rollScale': 0.5,
      'eosTmin': 2.0}" \
     -a 0.5 \
     -T 20.0 \
     -ed .70 \
     -rpoe 0.5 \
     -RotNS-runtype 30  2>&1  | tee  newHS.log


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
