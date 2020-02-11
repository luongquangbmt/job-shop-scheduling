#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 14:41:41 2020

@author: hoale
"""

"""
Single-stage scheduling problem with dissimilar parallel machines and sequence-
independent processing time.
1. Data from the supplementary resource of the paper: "Algorithms for Hybrid 
MILP/CP Models for a Class of Optimization Problems" 
(https://pubsonline.informs.org/doi/suppl/10.1287/ijoc.13.4.258.9733)

This file is inspired from repository: 
    https://github.com/caseypen/parallel_machine_scheduling/blob/master/mathematic_model/pmsp_gurobi.py
"""

import os
import numpy as np
import gurobipy as grb
from read_data import read_data
from original.original_milp_solver import _create_model
from gantt_plot import gantt_chart_plot, formulate_jobs_dict
import matplotlib.pyplot as plt

""" Single-stage job shop scheduling problem by Gurobi """
class SSJSP_Gurobi(object):
    def __init__(self):
        # setting the solver attributes
        self.schedules = {}
        self.sequence = {}
        
    """ Solve the model and formulate the result """
    def solve(self, job_num, machine_num, job_ids, request_times, due_times, process_intervals, processing_cost):
        solved = False
        model, assign, sequence, start_time = _create_model(job_num, machine_num, job_ids, request_times, due_times, 
                                                            process_intervals, processing_cost)
        
        """ Write a log file, cannot call in main() function """
        output_file = os.getcwd() + "/logs/original/original-jss-" + file_name + ".log"
        model.setParam(grb.GRB.Param.LogFile, output_file)
        
        try:
            # model.tune()
            model.optimize()
            if model.status == grb.GRB.Status.OPTIMAL:
                solved = True
                print("Optimal Schedule Cost: %i" % model.objVal)
                model.printStats()
                self._formulate_schedules(machine_num, job_ids, request_times, due_times, process_intervals, 
                                          processing_cost, assign, sequence, start_time)
            else:
                status_str = StatusDict[model.status]
                print("Optimization was stopped with status %s" %status_str)
                solved = False
                # self._formulate_schedules(machine_num, job_ids, request_times, due_times, process_intervals, 
                # processing_cost, assign, sequence, start_time)
        except grb.GurobiError as e:
            print("Error code " + str(e.errno) + ": " + str(e))
            
        return solved
            
    """ Formulate the result """
    def _formulate_schedules(self, machine_num, job_ids, request_times, due_times, process_intervals, processing_cost,
                             assign, sequence, start_time):
        # print("variables of start time from MILP: ", start_time)
        # print("sequence from MILP:", sequence)
        start_times = np.zeros(len(job_ids))
        assign_list = list()
        sequence_list = list()
        
        for i, j_id in enumerate(job_ids):
            self.schedules[j_id] = dict()
            self.schedules[j_id]["start"] = start_time[j_id].X
            
            for m in range(machine_num):
                if assign[j_id, m].x == 1:
                    self.schedules[j_id]["machine"] = m
                    self.schedules[j_id]["finish"] = start_time[j_id].x + process_intervals[j_id][m]
                    assign_list.append((j_id, m))
            start_times[i] = start_time[j_id].x
        
        # sequence of jobs vs jobs, sequence of (job, machine) like in hybrid-classical-jss.py
        for i_id in job_ids:
             for j_id in job_ids:
                 if i_id < j_id:
                     # if sequence[i_id, j_id].x > 0.5:
                     sequence_list.append((i_id, j_id))
        
        print("start_times of jobs: ", start_times)
        print("assign_list of job to machine: ", assign_list)
        # print("sequence_list of jobs sorted by increasing start time: ", sequence_list)
        self.sequence = job_ids[np.argsort(start_times)]

        return
        
        
if __name__ == '__main__':
    StatusDict = {getattr(grb.GRB.Status, s): s for s in dir(grb.GRB.Status) if s.isupper()}

    """ Read data """
    file_name, job_num, machine_num, processing_cost, process_intervals, request_times, due_times = read_data()
    
    # ID's jobs
    job_ids = np.arange(0, job_num, 1, dtype=np.int32)
    
    """ Create object """
    ssjsp_solver = SSJSP_Gurobi()
    
    """ Solve """
    solved = ssjsp_solver.solve(job_num, machine_num, job_ids, request_times, due_times, process_intervals, 
                                processing_cost)
    
    """ Display and Draw"""
    if solved:
        print("Schedules: ", ssjsp_solver.schedules)
        print("Sequence of jobs sorted by increasing start time: ", ssjsp_solver.sequence)
        
        job_dict = formulate_jobs_dict(job_ids, request_times, process_intervals)
        gantt_chart_plot(job_dict, ssjsp_solver.schedules, processing_cost, "Gurobi Solver for original problem")
        plt.show()
