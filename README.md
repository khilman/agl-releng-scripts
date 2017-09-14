# releng-scripts
This is an AGL job generation tool for [LAVA](https://staging.validation.linaro.org/static/docs/v2/).\
It is written in Python and uses jinja2 templates to generate yaml job files
following the LAVA specifications.

This tool **only** generates jobs. It does not provide a way for submitting jobs to a LAVA server.\
Please refer to the lava-tool [documentation](https://validation.linaro.org/static/docs/v2/lava-tool.html)
for submitting jobs.

## Prerequisites
- Python >= 2.7.1

## Usage instructions
The tool for generating job is located in the ./utils folder, it is named "create-jobs.py".

### create-jobs.py

Command line tool to generate AGL jobs for LAVA.

##### Required arguments:
- Machine name

##### Artifacts fetching from URL:
The tool will create an URL to fetch the build artifacts as follows: "URL_BASE/MACHINE_NAME".

Optionnal extra parameters can be used to extend the URL_BASE: `--jobid` and `--jobidx`.
The fetching URL will then be constructed like this: "URL_BASE/JOB_ID/JOB_INDEX/MACHINE_NAME"


The default URL_BASE is the AGL CI build repo.\
The job id and index parameters sould be passed to create a valid fetching URL from this repo.\
If using another URL these parameters can be omitted.

##### Example:
From default URL (https://download.automotivelinux.org/AGL/upload/ci/):\
`$ ./utils/create-jobs.py raspberrypi3 --jobid 10763 --jobidx 3`\
From other URLs:\
`$ ./utils/create-jobs.py raspberrypi3 --urlbase http://www.baylibre.com/pub/agl/ci/`\
`$ ./utils/create-jobs.py raspberrypi3 --urlbase https://download.automotivelinux.org/AGL/snapshots/master/latest/raspberrypi3/deploy/images/`\
`$ ./utils/create-jobs.py raspberrypi3 --urlbase https://download.automotivelinux.org/AGL/release/dab/4.0.0/raspberrypi3/deploy/images/`

The full list of arguments with default values is available using the helper:\
`$ ./utils/create-jobs.py --help`
