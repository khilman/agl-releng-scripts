## Using --callback-* arguments ##
- - - -

For each LAVA lab target, a configuration file must be created in this repo.
The file name must correspond to the LAVA lab name as registered in KernelCI.\
Using the argument "--callback-from LAB_NAME", the script will search for a file called "LAB_NAME.cfg" in this folder.\
Using the argument "--callback-to KCI_NAME", the script will search in the previous cfg file for a section called KCI_NAME. This section must contain three fields described below.

### Requirements: ###

* Filetype: .cfg
* Filename: <LAB_NAME>.cfg
    * [default] section
        * section = "The section containing the callback data to use by default"
    * [CUSTOM] section
        * backend_fqdn = "The FQDN of the kernelCI backend to callback"
        * lab_name = "The lab name as registered for the kernelCI backend"
        * lab_token = "The kernelCI backend lab token. Usually this is the 'LAVA description' string as shorthand of the token. Alternatively it can be the token itself."

Example file: _lab-mylab.cfg_
```
[default]
section = centralized-kci

[centralized-kci]
backend_fqdn = http(s)://api.centralized-kci.org
lab_name = lab-my-lab
lab_token = lab-my-lab-callback-centralized-kci

[my-dev-kci]
backend_fqdn = http(s)://api.my-dev-kci.org
lab_name = lab-my-lab
lab_token = f1d130b4-8198-4d34-9841-bad7d4ea64d9
```

_Warning:_\
If the lab_token is a LAVA description string, make sure that the actual token is registered in the LAVA interface and matches this string.
