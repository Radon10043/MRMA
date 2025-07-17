```py
@parameterized.expand(load_test_cases(1000))
def test1(self, job_list: list):
    """Metamorphic Relation: If the size of a job-list is 1, then the operation that moving the job at the top of this list to the end will not affect the output.
    - Source input: A `job_list` with a single job.
    - Input relation: Perform a "quantum expire" operation before flushing.
    - Output relation: The scheduler's output should be the same with or without the quantum expire operation.
    - Rationale: With only one job, moving it to the end of the queue doesn't change the scheduling order.
    """
    if job_list[0] != "1":
        return

    # Get source output
    source_op = SCHEDULE_OPERATIONS["FLUSH"]
    cmd_list = [SCHEDULE_PATH]
    cmd_list.extend(job_list)
    source_out = subprocess.check_output(cmd_list, input=source_op, text=True).split("\n")

    # Construct follow-up input
    follow_op = SCHEDULE_OPERATIONS["QUANTUM_EXPIRE"] + "\n" + SCHEDULE_OPERATIONS["FLUSH"]

    # Get follow-up output
    follow_out = subprocess.check_output(cmd_list, input=follow_op, text=True).split("\n")

    # Verification
    self.assertEqual(source_out, follow_out)
```