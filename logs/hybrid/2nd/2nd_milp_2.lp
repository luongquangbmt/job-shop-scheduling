\ Model SSJSP
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 
Subject To
 assigned_job_release_constraint[0]: start_time[0] >= 2
 assigned_job_release_constraint[1]: start_time[1] >= 3
 assigned_job_release_constraint[2]: start_time[2] >= 4
 assigned_job_due_constraint[0]: start_time[0] <= 2
 assigned_job_due_constraint[1]: start_time[1] <= 7
 assigned_job_due_constraint[2]: start_time[2] <= 10
 sequence_of_assigned_jobs[2,1]: sequence[1,2] + sequence[2,1] = 1
 valid_cut_by_big-M[1,2]: - 21 sequence[1,2] - start_time[1]
   + start_time[2] >= -15
 valid_cut_by_big-M[2,1]: - 21 sequence[2,1] + start_time[1]
   - start_time[2] >= -10
Bounds
Binaries
 sequence[1,2] sequence[2,1]
End
