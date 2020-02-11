#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 13:59:00 2020

@author: hoale
"""

"""
Single-stage scheduling problem with dissimilar parallel machines and sequence-
independent processing time.
1. Data from the supplementary resource of the paper: "Algorithms for Hybrid 
MILP/CP Models for a Class of Optimization Problems" 
(https://pubsonline.informs.org/doi/suppl/10.1287/ijoc.13.4.258.9733)
"""

"""
This file is the hybrid classical approaches: MILP and CP
"""

import os
import numpy as np
import gurobipy as grb
from read_data import read_data
from hybrid.hybrid_relaxed_milp import _create_milp_model
from hybrid.hybrid_cp_solver import _create_cp_model
# from hybrid.hybrid_milp_solver import _create_model
from gantt_plot import gantt_chart_plot, formulate_jobs_dict, formulate_sequence_dict
import matplotlib.pyplot as plt


""" Single-stage job shop scheduling problem by hybrid method of Gurobi MILP and Docplex CP """
class SSJSP_Hybrid(object):
    def __init__(self):
        # setting the solver attributes
        self.schedules = {}
        self.sequence = {}
        
    """ Solve the model and formulate the result """
    def solve(self, file_name, all_jobs, job_num, all_machines, machine_num, job_ids, request_times, due_times, 
              process_intervals, processing_cost):
        solved = False
        k = 0
        milp_model, assign, start_time = _create_milp_model(job_num, machine_num, job_ids, request_times, 
                                                                 due_times, process_intervals, processing_cost)
        
        """ Write a log file, cannot call in main() function """
        output_file = os.getcwd() + "/logs/hybrid/hybrid-jss-" + file_name + ".log"
        milp_model.setParam(grb.GRB.Param.LogFile, output_file)
        
        """ Hybrid strategy """
        try:
            while not solved:
                print("-----------------------------------------ITERATION:--------------------------------", k+1)
                # milp_model.update()
                # milp_model.tune()
                milp_model.optimize()
                if k > 0:
                    print("After getting integer cuts %i:" %(k + 1))

                if milp_model.status == grb.GRB.Status.OPTIMAL:
                    """ Check the feasibility subproblem by MILP or CP model """
                    res, cp_start_time = self._feasi_by_cp(all_jobs, job_ids, job_num, all_machines, request_times, due_times, 
                                            process_intervals, assign)
                    
                    """ Feasible, no Optimal due to no objective function of CP model """
                    if res.is_solution():
                        print(res.get_solve_status())
                        solved = True
                        print("Optimal Schedule Cost: %i" % milp_model.objVal)
                        milp_model.printStats()
                        sequence = formulate_sequence_dict(all_jobs, all_machines, assign, res, cp_start_time)
                        self._formulate_schedules(all_machines, job_ids, request_times, due_times, process_intervals, 
                                                  assign, sequence, start_time)
                    elif not res.is_solution():
                        """ Infeasible """
                        k += 1
                        """ Adding integer cuts """
                        # 1. Creation of set of elements x[i,m] == 1
                        set_xim = [i for i in range(job_num) for m in range(machine_num) if assign[(i,m)].x == 1]
                        # 2. Add constraint to MILP model
                        milp_model.addConstrs((grb.quicksum([assign[(i,m)] for i in set_xim 
                                                              for m in range(machine_num) 
                                                              if assign[(i,m)].x == 1]) <= len(set_xim) - 1
                                                for m in range(machine_num)), name="integer cut")
                else:
                    status_str = StatusDict[milp_model.status]
                    print("Optimization was stopped with status %s" %status_str)
                    milp_model.params.DualReductions = 0
                    milp_model._vars = assign, start_time
                    milp_model.Params.lazyConstraints = 1
                    solved = True
            
        except grb.GurobiError as e:
            print("Error code " + str(e.errno) + ": " + str(e))
            
        return solved         
    
    """ Feasibility by CP model """
    def _feasi_by_cp(k, all_jobs, job_ids, job_num, all_machines, r_times, d_times, p_intervals, assign):
        model, start_time = _create_cp_model(all_jobs, job_ids, job_num, all_machines, r_times, d_times, p_intervals, assign)
        cp_model, cp_start_time = _create_cp_model(all_jobs, job_ids, job_num, all_machines, request_times, due_times, 
                                                   process_intervals, assign)
    
        # Solve CP model
        print("Solving CP model for feasibility subproblem....")
        res = cp_model.solve()
        print("Solution of CP model: ")
        res.print_solution()
        
        """ Export the CPO file contains constraint requirements of CP model """
        out_file = os.getcwd() + "/logs/hybrid/hybrid-jss-milp-cp" + file_name + str(k) + ".cpo"
        file_object  = open(out_file, "w")
        cp_model.export_as_cpo(out_file)
        file_object.close()
        print("Finished writing CP outputs into .cpo file\n")
        
        return res, cp_start_time
    
    """ Formulate the result """
    def _formulate_schedules(self, all_machines, job_ids, request_times, due_times, process_intervals, assign, sequence, 
                             start_time):
        """
        variable assign is actually a true feasible assignment, this variable is different from that of original solver
        in gurobi-jss.py
        """
        # print("start-time from MILP: ", start_time)
        # print("sequence from CP:", sequence)
        
        start_times = np.zeros(len(job_ids))
        assign_list = list()
        
        for i, j_id in enumerate(job_ids):
            self.schedules[j_id] = dict()
            
            for m in all_machines:
                if assign[j_id, m].x == 1:
                    self.schedules[j_id]["machine"] = m
                    self.schedules[j_id]["start"] = sequence[(j_id, m)].start
                    self.schedules[j_id]["finish"] = sequence[(j_id, m)].end
                    assign_list.append((j_id, m))
                    start_times[i] = sequence[(j_id, m)].start

        print("start times of jobs: ", start_times)
        print("assign list of jobs to machines: ", assign_list)
        self.sequence = job_ids[np.argsort(start_times)]

        return
    
    
if __name__ == '__main__':
    StatusDict = {getattr(grb.GRB.Status, s): s for s in dir(grb.GRB.Status) if s.isupper()}
    
    """ Read data """
    file_name, job_num, machine_num, processing_cost, process_intervals, request_times, due_times = read_data()
    
    # ID's jobs
    job_ids = np.arange(0, job_num, 1, dtype=np.int32)
    all_jobs = range(job_num)
    all_machines = range(machine_num)
    
    ssjsp_solver = SSJSP_Hybrid()
    solved = ssjsp_solver.solve(file_name, all_jobs, job_num, all_machines, machine_num, job_ids, request_times, 
                                due_times, process_intervals, processing_cost)
    
    if solved:
        print("Schedules: ", ssjsp_solver.schedules)
        print("Sequence after sorted by increasing start time: ", ssjsp_solver.sequence)
        
        job_dict = formulate_jobs_dict(job_ids, request_times, process_intervals)
        gantt_chart_plot(job_dict, ssjsp_solver.schedules, processing_cost, "Hybrid Strategy of MILP and CP")
        plt.show()
