#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 17:22:02 2020

@author: hoale
"""

"""
This file contains CP solver based on DOCPLEX IBM
"""

""" IBM CPLEX """
from docplex.cp.model import CpoModel, start_of, end_of, size_of

""" Creation of CP model with constraints (subproblem 2) """
def _create_cp_model(all_jobs, job_ids, job_num, all_machines, r_times, d_times, p_intervals, assign):
    """ Prepare the index for decision variables """
    # typle of jobs, form (job_0, job_1, ...)
    jobs = tuple(job_ids)
    
    """ Parameters model (dictionary) """
    # 1. release time
    release_time = dict(zip(jobs, tuple(r_times)))
    # 2. due time
    due_time = dict(zip(jobs, tuple(d_times)))
    # 3. processing time
    process_time = dict(zip(jobs, tuple(p_intervals)))
    
    """ Creation of the CP model container """
    cp_model = CpoModel(name="CP-Model")
    
    """ Creation of variables """
    # for j_id in all_jobs:
    #     for m_id in all_machines:
    #         if assign[(j_id, m_id)].x == 1:
    #             print(assign[(j_id, m_id)])
    # 1. Variable subscript z_i represents machine selected to process job i
    z = {j_id: m_id for j_id in all_jobs for m_id in all_machines if assign[(j_id, m_id)].x == 1}
    # print("z: ", z)

    """ DOCPLEX """
    # 1. list of interval variable, is a list of start time of jobs (i.start in CP model)         
    start_time_cp = [cp_model.interval_var(size=process_time[j_id][z[j_id]], 
                                           name="start-time-J{}".format(j_id)) for j_id in all_jobs]
    # if assign[(j_id, z[j_id])].x == 1]
    
    """ Create constraints """
    # 1. job release time constraint
    cp_model.add(start_of(start_time_cp[i]) >= release_time[i] for i in jobs)
   
    # 2. job due time constraint
    cp_model.add(start_of(start_time_cp[i]) <= due_time[i] - process_time[i][z[i]] for i in jobs)

    # 3. duration of processing one job constraint
    cp_model.add(size_of(start_time_cp[i]) == process_time[i][z[i]] for i in jobs)
    
    # 4. assignment of a job to a specific machine as well as sequence of jobs assigned to same machine
    # "requires" in OPL construct
    # job i requires unary resource corresponding to machine which was assigned from MILP
    # force no overlap for jobs      
    # Constrain jobs to no overlap on each machine
    # Force no overlap for jobs executed on a same machine
    # disjunctive resource (unary resource): end(J1) <= start(J2) ||end(J2) <= start(J1)
    for job_id1 in range(job_num - 1):
        for job_id2 in range(job_id1 + 1, job_num):
            # print("job id1 & job id2", job_id1, job_id2)
            if z[job_id1] == z[job_id2]:
                cp_model.add(cp_model.logical_or(
                    end_of(start_time_cp[job_id1]) <= start_of(start_time_cp[job_id2]), 
                    end_of(start_time_cp[job_id2]) <= start_of(start_time_cp[job_id1])))

    return cp_model, start_time_cp