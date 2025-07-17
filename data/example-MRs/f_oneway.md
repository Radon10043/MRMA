```py
@parameterized.expand(load_test_cases)
def test1(self, g1: list, g2: list):
    """Metamorphic Relation: Changing the order of the samples, the result should not change.
    - Source input: Two groups of samples, `g1` and `g2`.
    - Input relation: Create `follow_g1` and `follow_g2` by permuting the elements within `g1` and `g2` respectively.
    - Output relation: The p-value from `f_oneway(follow_g1, follow_g2)` must be almost equal to the p-value from `f_oneway(g1, g2)`.
    - Rationale: The F-test for one-way ANOVA is based on the variance between and within groups, which is not affected by the order of samples within each group.
    """
    # Get source output
    source_out = f_oneway(g1, g2).pvalue

    # Construct follow-up input
    follow_g1 = np.random.permutation(g1)
    follow_g2 = np.random.permutation(g2)

    # Get follow-up output
    follow_out = f_oneway(follow_g1, follow_g2).pvalue

    # Verification
    self.assertAlmostEqual(source_out, follow_out)
```