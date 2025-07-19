# MR-CoT-RAG

gen_driver.json:

- candidate: MR candidate file path.
- xxx
- build: build settings.
  - prefix: prefix wanna add to the head of candidate.
  - srcdir: only applicable for java file, files and directories under `srcdir` will all copy to `test_driver/src`

```json
{
    "candidate": "$PROJECT/workdir/dryrun/ACMS/1752722280068/mr_candidate.java",
    "agent": {
        "model": "gemini-2.5-pro",
        "temperature": 1.0,
        "top_p": 1.0,
        "prompts": {
            "system": "$PROJECT/data/prompts/driver/system.md",
            "user": [
                "$PROJECT/data/prompts/driver/user1.md",
                "$PROJECT/data/prompts/driver/user2.md"
            ]
        }
    },
    "build": {
        "source": ""
    },
    "max_iter": 10
}
```

TODO:
[ ]: Add `make check` to check whether `api_key` or `base_url` maybe leaked
[ ]: Use Sphinx to generate documents
[ ]: Should we use newer version of Lucene, Jodatime, JAMA, etc.?