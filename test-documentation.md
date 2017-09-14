# Test documentation

### Test parsing
All the tests templates within ./templates/tests/ are parsed by the tools.

### New test definition
Just create a new jinja2 template file within the tests folder containing the test definition.\
Some examples of test definitions are provided in the templates/examples/ folder.

###  Generate test plans
Use the create-jobs.py script to generate test plans. Just use the `--test` parameter with the
test name or `--test all` to run all tests.

### Examples
Add new test definition:\
`$ cp templates/examples/test_local_inline.jinja2 templates/tests/`\
Generate test job from the new test definition:\
`$ ./utils/create-jobs.py raspberrypi3 --test test_local_inline`
