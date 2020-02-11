#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 17:36:05 2020

@author: hoale
"""

"""
This file contains function to read data from file
"""
import os

def read_data():
    """ Read data file """
    # file_name = "job3_machine2_ds1"
    # file_name = "job3_machine2_ds2"
    # file_name = "job7_machine3_ds1"
    # file_name = "job7_machine3_ds2"
    # file_name = "job8_machine8_ds1"
    # file_name = "job12_machine3_ds1"
    # file_name = "job12_machine3_ds2"
    # file_name = "job15_machine5_ds1"
    # file_name = "job15_machine5_ds2"
    file_name = "job20_machine5_ds1"
    # file_name = "job20_machine5_ds2"
    
    input_file = os.getcwd() + "/data/" + file_name
    
    with open(input_file) as f:
        content = f.readlines()
        
    content = [x.strip() for x in content]
    """
    #jobs, #machines
    list of processing costs
    list of processing interval
    """
    job_num, machine_num = map(int, content[0].split())
    processing_cost = [[int(item) for item in content[idx].split()] for idx in 
                       range(1, job_num+1)]
    process_intervals = [[int(item) for item in content[idx].split()] for idx in 
                         range(job_num+1, 2*job_num+1)]
    request_times = [int(item) for item in content[2*job_num+1].split()]
    due_times = [int(item) for item in content[-1].split()]
    
    print("-------Reading file------------:\n")
    print("number of jobs: ", job_num)
    print("number of machines:", machine_num)
    print("processing cost:", processing_cost)
    print("processing time:", process_intervals)
    print("release time:", request_times)
    print("due time:", due_times)

    return file_name, job_num, machine_num, processing_cost, process_intervals, \
            request_times, due_times


if __name__ == "__main__":
    read_data()
