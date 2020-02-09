\ Model SSJSP
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 
Subject To
 assigned_job_release_constraint[0]: start_time[0] >= 2
 assigned_job_release_constraint[1]: start_time[1] >= 3
 assigned_job_release_constraint[2]: start_time[2] >= 4
 assigned_job_due_constraint[0]: start_time[0] <= 6
 assigned_job_due_constraint[1]: start_time[1] <= 7
 assigned_job_due_constraint[2]: start_time[2] <= 5
 sequence_of_assigned_jobs[1,0]: sequence[0,1] + sequence[1,0] = 1
 valid_cut_by_big-M[0,1]: - 21 sequence[0,1] - start_time[0]
   + start_time[1] >= -11
 valid_cut_by_big-M[1,0]: - 21 sequence[1,0] + start_time[0]
   - start_time[1] >= -15
Bounds
Binaries
 sequence[0,1] sequence[1,0]
End
