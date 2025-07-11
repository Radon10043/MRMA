```python
@parameterized.expand(load_test_cases)
def test1(self, tc: str):
    """Metamorphic Relation: Adding a new line containing only a comma increases the output line count by one.
    - Source input: A string of code `tc`.
    - Input relation: Create `tc'` by appending a newline character followed by a comma to `tc`.
    - Output relation: The number of lines in `print_tokens(tc')` must be exactly one more than the number of lines in `print_tokens(tc)`.
    - Rationale: A comma is a distinct token. The `print_tokens` program should recognize it and print its token information on a new line, thus incrementing the total line count of the output by one.
    """
    # Get source output
    source_out = subprocess.check_output(PRINT_TOKENS_PATH, input=tc, text=True).split("\n")

    # Construct follow-up input
    follow_tc = tc + "\n,"

    # Get follow-up output
    follow_out = subprocess.check_output(PRINT_TOKENS_PATH, input=follow_tc, text=True).split("\n")

    # Verification
    self.assertEqual(len(source_out) + 1, len(follow_out))

@parameterized.expand(load_test_cases)
def test2(self, tc: str):
    """Metamorphic Relation: Deleting all comments from the input string should not change the output.
    - Source input: A string of code `tc` that may contain comments.
    - Input relation: Create `tc'` by removing all semicolon-style comments from `tc`.
    - Output relation: `print_tokens(tc)` must equal `print_tokens(tc')`.
    - Rationale: The program functions as a tokenizer. Comments are typically non-functional and should be ignored during lexical analysis, thus not affecting the sequence of generated tokens.
    """
    # Get source output
    source_out = subprocess.check_output(PRINT_TOKENS_PATH, input=tc, text=True).split("\n")

    # Construct follow-up input
    follow_tc = tc.split("\n")
    for i in range(len(follow_tc)):
        follow_tc[i] = follow_tc[i].split(";")[0]
    follow_tc = "\n".join(follow_tc)

    # Get follow-up output
    follow_out = subprocess.check_output(PRINT_TOKENS_PATH, input=follow_tc, text=True).split("\n")

    # Verification
    self.assertEqual(source_out, follow_out)

@parameterized.expand(load_test_cases)
def test3(self, tc: str):
    """Metamorphic Relation: Adding a comment to the input string should not change the output.
    - Source input: A string of code `tc`.
    - Input relation: Create `tc'` by appending a comment to the end of `tc`.
    - Output relation: `print_tokens(tc)` must equal `print_tokens(tc')`.
    - Rationale: The program functions as a tokenizer. Comments are typically non-functional and should be ignored during lexical analysis, thus not affecting the sequence of generated tokens.
    """
    # Get source output
    source_out = subprocess.check_output(PRINT_TOKENS_PATH, input=tc, text=True).split("\n")

    # Construct follow-up input
    follow_tc = tc + "; Comment!"

    # Get follow-up output
    follow_out = subprocess.check_output(PRINT_TOKENS_PATH, input=follow_tc, text=True).split("\n")

    # Verification
    self.assertEqual(source_out, follow_out)
```