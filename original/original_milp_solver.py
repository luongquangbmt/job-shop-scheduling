#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 17:44:52 2020

@author: hoale
"""

""" 
This file contains solver for original problem by GUROBI
"""

import gurobi as grb

""" Creation of MILP model with constraints """
def _create_model(job_num, machine_num, job_ids, r_times, d_times, p_intervals, p_cost):
    """ Prepare the index for decision variables """
    # start time of process
    jobs = tuple(job_ids)
    # print("inside:", jobs)
    machines = tuple(range(machine_num))
    # print(machines)
    # sequence of processing jobs: tuple list
    job_pairs = [(i, j) for i in jobs for j in jobs if i != j]
    # print(job_pairs)
    # assignment of jobs on machines
    job_machine_pairs = [(i, m) for i in jobs for m in machines]
    # print(job_machine_pairs)
    # dissimilar parallel machine-machine pair
    machine_pairs = [(m, n) for m in machines for n in machines if m != n]
    
    """ Parameters model (dictionary) """
    # 1. release time
    release_time = dict(zip(jobs, tuple(r_times)))
    # print("release time:", release_time)
    # 2. due time
    due_time = dict(zip(jobs, tuple(d_times)))
    # print("due time:", due_time)
    # 3. processing time
    process_time = dict(zip(jobs, tuple(p_intervals)))
    # print("process time:", process_time)
    # 4. processing cost
    job_cost = dict(zip(jobs, tuple(p_cost)))
    # print("processing cost:", job_cost)
    # 5. define BigU
    U = sum([max(p_intervals[i]) for i in range(job_num)])
    # print("test U:", U)
    
    """ Create model """
    model = grb.Model("SSJSP")
    
    """ Create decision variables """
    # 1. Assignments of jobs on machines
    x = model.addVars(job_machine_pairs, vtype=grb.GRB.BINARY, name="assign")
    # 2. Sequence (Order) of executing jobs
    y = model.addVars(job_pairs, vtype=grb.GRB.BINARY, name="sequence")
    # 3. Start time of executing each job (ts = time_start)
    ts = model.addVars(jobs, lb=0, name="start_time")

    """ Create the objective function """
    model.setObjective(grb.quicksum([(job_cost[i][m]*x[(i,m)]) for m in machines for i in jobs]),
                       sense=grb.GRB.MINIMIZE)
    
    """ Create constraints """
    # 1. job release time constraint
    model.addConstrs((ts[i] >= release_time[i] for i in jobs), name="job release constraint")
    # 2. job due time constraint
    model.addConstrs((ts[i] <= due_time[i] - grb.quicksum([process_time[i][m]*x[(i,m)] for m in machines]) 
                      for i in jobs), name="job due constraint")
    # 3. one job is assigned to one and only one machine
    model.addConstrs((grb.quicksum([x[(i,m)] for m in machines]) == 1 for i in jobs), 
                     name="job non-splitting constraint")
    # 4. job 'j' is processed after job 'i' when both jobs are assigned to same machine
    model.addConstrs((y[(i,j)] + y[(j,i)] >= x[(i,m)] + x[(j,m)] - 1 for m in machines for (i,j) in job_pairs if j > i), 
                      name="assignment-sequencing vars constraint")
    # 5. sequencing constraint
    model.addConstrs((ts[j] >= ts[i] + grb.quicksum([process_time[i][m]*x[(i,m)] for m in machines]) 
                      - U*(1 - y[(i,j)]) for (i,j) in job_pairs), 
                     name="sequence constraint")
    # 6. either job 'i' is processed before job 'j' or vice versa
    model.addConstrs((y[(i,j)] + y[(j,i)] <= 1 for (i,j) in job_pairs if j > i), name="sequence of jobs")
    # 7. sequencing varibles = 0 when job 'i' and 'j' are assigned to different machines
    model.addConstrs((y[(i,j)] + y[(j,i)] + x[(i,m)] + x[(j,n)] <= 2 
                      for (m,n) in machine_pairs for (i,j) in job_pairs if j > i), 
                     name="different machine constraint")
    
    return model, x, y, ts
