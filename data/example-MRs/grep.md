```py
@parameterized.expand(load_test_cases)
def test2(self, pattern: str, file: str):
    """Metamorphic Relation: Swapping the case of a search pattern should result in an equal or greater number of matches when the search is case-insensitive.
    - Source input: A pattern file `p` and a file to be searched `f`.
    - Input relation: Create a new pattern file `p'` by swapping the case of all characters in the original pattern file `p`.
    - Output relation: The number of lines returned by `grep --ignore-case -f p f` must be less than or equal to the number of lines returned by `grep --ignore-case -f p' f`.
    - Rationale: The program is performing a case-insensitive search due to the `--ignore-case` flag. Therefore, altering the capitalization of the search patterns should not, in a correct implementation, change the number of matched lines. An assertion of equality or greater length serves as a valid check for this property.
    """
    # Get source output
    process = os.popen(f"{GREP_PATH} --ignore-case -f {pattern} {file}")
    source_out = process.readlines()
    process.close()

    # Construct follow-up input
    follow_pattern = os.path.join(os.path.dirname(pattern), "follow_pattern.txt")
    with open(follow_pattern, mode="w") as ff:
        with open(pattern) as sf:
            ff.write(sf.read().swapcase())

    # Get follow-up output
    process = os.popen(f"{GREP_PATH} --ignore-case -f {follow_pattern} {file}")
    follow_out = process.readlines()
    process.close()

    # Verification
    self.assertGreaterEqual(len(follow_out), len(source_out))
```