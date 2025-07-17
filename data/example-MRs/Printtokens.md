```py
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