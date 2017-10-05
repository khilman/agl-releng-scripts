# Test documentation

### Test parsing
All the tests templates within <releng-scripts>/templates/tests/ are parsed by the tools
can be added to a test plan.

### Add test definition
Just create a new jinja2 template file within the tests folder containing the tests definitions.\
A test example is provided in the doc/ folder pointing to the remote
test definition repository: [https://git.automotivelinux.org/src/qa-testdefinitions/tree/](qa-testdefinitions).

###  Generate test plans
Use the create-jobs.py script to generate test plans. Just use the `--test` parameter with the
test name or `--test all` to run all tests.

### Examples
Add new test definition:\
`$ cp doc/test_remote_scripts.jinja2 templates/tests/`\
Generate test job from the new test definition:\
`$ ./utils/create-jobs.py raspberrypi3 --test test_remote_scripts`
