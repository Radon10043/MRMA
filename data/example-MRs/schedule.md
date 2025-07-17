```py
@parameterized.expand(load_test_cases(1000))
def test1(self, job_list: list):
    """Metamorphic Relation: If the size of a job-list is 1, then the operation that moving the job at the top of this list to the end will not affect the output.
    - Source input: A `job_list` with a single high-priority job.
    - Input relation: Perform a "quantum expire" operation, which moves the current job to the end of its priority queue.
    - Output relation: The scheduler's output after a flush should be the same with or without the quantum expire operation.
    - Rationale: When there is only one job, moving it to the end of the queue results in the same queue state, so the final schedule is unchanged.
    """
    high_priority_index = int(PRIORITY_LEVEL["HIGH"]) - 1
    if int(job_list[high_priority_index]) != 1:
        return

    # Get source output
    source_op = [SCHEDULE_OPERATIONS["FLUSH"]]
    cmd_list = [SCHEDULE_PATH]
    cmd_list.extend(job_list)
    source_out = subprocess.check_output(cmd_list, input=" ".join(source_op), text=True).split("\n")

    # Construct follow-up input
    follow_op = [SCHEDULE_OPERATIONS["QUANTUM_EXPIRE"], SCHEDULE_OPERATIONS["FLUSH"]]

    # Get follow-up output
    follow_out = subprocess.check_output(cmd_list, input=" ".join(follow_op), text=True).split("\n")

    # Verification
    self.assertEqual(source_out, follow_out)
```