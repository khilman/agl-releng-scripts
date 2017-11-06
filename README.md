# releng-scripts
This is an AGL job generation tool for [LAVA](https://staging.validation.linaro.org/static/docs/v2/).\
It is written in Python and uses jinja2 templates to generate yaml job files
following the LAVA specifications.

This tool **only** generates jobs. It does not provide a way for submitting jobs to a LAVA server.\
Please refer to the lava-tool [documentation](https://validation.linaro.org/static/docs/v2/lava-tool.html)
for submitting jobs.

## Prerequisites
- Python >= 2.7.1
- jinja >= 2.9
    - You can check if a version is/was installed with pip using: ```pip show jinja2```
    - If the version is too old, you can update it using: ```sudo pip install --upgrade jinja2```

## Usage instructions
The tool for generating job is located in the ./utils folder, it is named "create-jobs.py".

### create-jobs.py

Command line tool to generate AGL jobs for LAVA.

##### Required arguments:
- ```./utils/create-jobs.py --machine machine-name```
    - Available machine names: ```{dra7xx-evm,qemux86-64,porter,m3ulcb,raspberrypi3}```
    - For an up to date list of machine names run: ```./utils/create-jobs.py --help```

##### Artifacts fetching from URL:
Amongst other things, this tool is used to generate URLs for fetching build artifacts from specific locations.\
The default location is: https://download.automotivelinux.org/AGL/\
The default build is dab version 4.0.2

The user can override these defaults using the command line:
- ```--url <release, daily, ci or http://my-custom-url....>```
    - Available url options and their corresponding URL:
        - release: https://download.automotivelinux.org/AGL/release/
        - daily: https://download.automotivelinux.org/AGL/snapshots/
        - ci: https://download.automotivelinux.org/AGL/upload/ci/

If using the url argument the user has to specify other arguments depending on the url:
- release: ```--branch and --version```
- daily: ```--branch and --version```
- ci: ```--changeid and --patchset```

If using a custom url these argument are not used and should not be set. The tool will suppose that the custom url points directly to build artifacts for the target machine.

_Examples:_
```
./utils/create-jobs.py --machine m3ulcb
./utils/create-jobs.py --machine qemux86-64
./utils/create-jobs.py --url release --branch eel --version 4.99.1 --machine m3ulcb
./utils/create-jobs.py --url release --branch eel --version 4.99.1 --machine qemux86-64
./utils/create-jobs.py --url daily --branch master --version latest --machine m3ulcb
./utils/create-jobs.py --url daily --branch master --version latest --machine raspberrypi3
./utils/create-jobs.py --url ci --changeid 11533 --patchset 2 --machine raspberrypi3
./utils/create-jobs.py --url ci --changeid 11533 --patchset 2 --machine m3ulcb
./utils/create-jobs.py --url http://baylibre.com/pub/agl/ci/raspberrypi3 --machine raspberrypi3
```
The full list of arguments with default values is available using the helper:\
`$ ./utils/create-jobs.py --help`

##### Add tests to a job
To add tests to a job description please refer to the specific documentation: [releng-scripts-folder]/doc/test-documentation.md
