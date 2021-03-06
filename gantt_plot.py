#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 11:35:51 2020

@author:
"""

""" Plotting the Gantt chart (this file is inspired from repository: 
    https://github.com/caseypen/parallel_machine_scheduling/blob/master/mathematic_model/gantt_plot.py 
"""

import collections
import matplotlib.pyplot as plt

def gantt_chart_plot(JOBS, SCHEDULE, Machine_available, Title):
    bw = 0.3
    plt.figure(figsize=(12, 0.7*(len(JOBS.keys()))))
    idx = 0
    for j in sorted(JOBS.keys()):
        x = 0
        # y = JOBS[j]['release']
        # plt.fill_between([x,y],[idx-bw,idx-bw],[idx+bw,idx+bw], color='cyan', alpha=0.6, label="release constraint")
        x = SCHEDULE[j]['start']
        y = SCHEDULE[j]['finish']
        plt.fill_between([x,y],[idx-bw,idx-bw],[idx+bw,idx+bw], color='red', alpha=0.5, label="process interval")
        plt.plot([x,y,y,x,x], [idx-bw,idx-bw,idx+bw,idx+bw,idx-bw],color='k')
        plt.text((SCHEDULE[j]['start'] + SCHEDULE[j]['finish'])/2.0,idx,
            'Job ' + str(j), color='grey', weight='bold',
            horizontalalignment='center', verticalalignment='center')
        idx += 1

    plt.ylim(-0.5, idx-0.5)
    plt.title('Job Schedule '+ Title)
    plt.xlabel('Time')
    plt.ylabel('Jobs')
    plt.yticks(range(len(JOBS)), JOBS.keys())
    plt.grid()
    xlim = plt.xlim()

    # # order machine for plotting nicely
    MACHINES = sorted(set([SCHEDULE[j]['machine'] for j in JOBS.keys()]))
    
    plt.figure(figsize=(12, 0.7*len(MACHINES)))
    for j in sorted(JOBS.keys()):
        idx = MACHINES.index(SCHEDULE[j]['machine'])
        x = 0
        # y = Machine_available[idx]
        # y = Machine_available[j][idx]
        # plt.fill_between([x,y],[idx-bw,idx-bw],[idx+bw,idx+bw], color='green', alpha=0.5)
        x = SCHEDULE[j]['start']
        y = SCHEDULE[j]['finish']
        plt.fill_between([x,y],[idx-bw,idx-bw],[idx+bw,idx+bw], color='red', alpha=0.5)
        plt.plot([x,y,y,x,x], [idx-bw,idx-bw,idx+bw,idx+bw,idx-bw],color='k')
        plt.text((SCHEDULE[j]['start'] + SCHEDULE[j]['finish'])/2.0,idx,
            'Job ' + str(j), color='grey', weight='bold',
            horizontalalignment='center', verticalalignment='center')
    plt.xlim(xlim)
    plt.ylim(-0.5, len(MACHINES)-0.5)
    plt.title('Machine Schedule '+ Title)
    plt.yticks(range(len(MACHINES)), MACHINES)
    plt.ylabel('Machines')
    plt.grid()

def formulate_jobs_dict(job_ids, release_times, process_intervals):
    job_dict = {}
    for idx, j_id in enumerate(job_ids):
        job_dict[j_id] = {}
        job_dict[j_id]['release'] = release_times[idx]
        job_dict[j_id]['duration'] = process_intervals[idx]
    return job_dict

def formulate_schedule_dict(job_ids, release_times, process_intervals, wait_times, machine_dispatches):
    schedule_dict = {}
    for idx, j_id in enumerate(job_ids):
        schedule_dict[j_id] = {}
        schedule_dict[j_id]['start'] = release_times[idx]+wait_times[idx]
        schedule_dict[j_id]['finish'] = release_times[idx]+process_intervals[idx]+wait_times[idx]
        schedule_dict[j_id]['machine'] = machine_dispatches[idx]
    return schedule_dict

""" Construction of sequence of jobs from cp_start_time variable of CP model"""
def formulate_sequence_dict(all_jobs, all_machines, assign, result, start_time):
    # Named tuple to store information about created variables.
    job_type = collections.namedtuple('job_type', 'start end interval')
        
    sequence = {}
    for m_id in all_machines:
        for j_id in all_jobs:
            # Check assign job j_id already to machine m_id
            if assign[(j_id,m_id)].x == 1:
                # print("assign job %i to machine %i" % (j_id, m_id))
                # print("sequence:", m_id, j_id, result.get_value(start_time[j_id]))
                # Take value of decision variable from CP model
                value = result.get_value(start_time[j_id])
                # value in form (start, end, size, length)
                sequence[(j_id, m_id)] = job_type(start=value[0], interval=value[0]+value[2], end=value[1])
        
    return sequence
