#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 17:19:08 2020

@author: hoale
"""

"""
This file contains relaxed MILP solver
"""

import gurobipy as grb

""" Creation of relaxed MILP model with constraints (subproblem 1) """
def _create_milp_model(job_num, machine_num, job_ids, r_times, d_times, p_intervals, p_cost):
    """ Prepare the index for decision variables """
    # index of jobs
    jobs = tuple(job_ids)
    # index of machines
    machines = tuple(range(machine_num))
    # assignment of jobs on machines
    job_machine_pairs = [(i, m) for i in jobs for m in machines]
    
    """ Parameters model (dictionary) """
    # 1. release time
    release_time = dict(zip(jobs, tuple(r_times)))
    # 2. due time
    due_time = dict(zip(jobs, tuple(d_times)))
    # 3. processing time
    process_time = dict(zip(jobs, tuple(p_intervals)))
    # 4. processing cost
    job_cost = dict(zip(jobs, tuple(p_cost)))
    
    """ Create model """
    model = grb.Model("SSJSP")
    output_file = "gurobi-jss.log" + "_" + str(job_num) + "_" + str(machine_num)
    model.setParam(grb.GRB.Param.LogFile, output_file)
    
    """ Create decision variables """        
    # 1. Assignments of jobs on machines
    x = model.addVars(job_machine_pairs, vtype=grb.GRB.BINARY, name="assign")
    # 2. Start time of executing each job (ts = time_start)
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
    # 4. A valid cut, it tightens LP relaxation, total processing time of all jobs assigned to same machine
    # less than diff of latest due date & earliest release date
    model.addConstrs((grb.quicksum([x[(i,m)]*process_time[i][m] for i in jobs]) <= max(due_time.values()) - 
                      min(release_time.values()) for m in machines), name="total processing time of all jobs")
    
    return model, x, ts  