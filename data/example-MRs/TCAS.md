```py
@parameterized.expand(load_test_cases)
def test1(self, vals: list):
    """Metamorphic Relation: If the relation of the Own_Tracked_Alt and Other_Tracked_Alt is not changed, meanwhile other parameter values are not changed too, then the outputs of the TCAS should be the same.
    - Source input: A list of TCAS parameters `vals`.
    - Input relation: Create `follow_vals` by scaling both `Own_Tracked_Alt` and `Other_Tracked_Alt` by the same factor, keeping their relative difference proportional.
    - Output relation: The TCAS output for `follow_vals` must be identical to the output for `vals`.
    - Rationale: The TCAS advisory logic depends on the relative altitude difference, not the absolute altitudes. Scaling both altitudes maintains this relationship.
    """
    # Get source output
    cmd_list = [TCAS_PATH]
    tmp_list = [str(x) for x in vals]
    cmd_list.extend(tmp_list)
    source_out = subprocess.check_output(cmd_list, text=True).split("\n")

    # Construct follow-up input
    follow_vals = vals.copy()
    follow_vals[INDEX["Own_Tracked_Alt"]] += 100
    follow_vals[INDEX["Other_Tracked_Alt"]] += 100

    # Get follow-up output
    cmd_list = [TCAS_PATH]
    tmp_list = [str(x) for x in follow_vals]
    cmd_list.extend(tmp_list)
    follow_out = subprocess.check_output(cmd_list, text=True).split("\n")

    # Verification
    self.assertEqual(source_out, follow_out)
```