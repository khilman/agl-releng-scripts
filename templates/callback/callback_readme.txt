## The callbacks info must be in this repo ##
- - - -

### Requirements: ###

* Filetype: .cfg
* Filename: <LAB_NAME>.cfg
    * [default] section
    * backend_fqdn = "The FQDN of the kernelCI backend to callback"
    * lab_name = "The lab name as registered for the kernelCI backend"
    * lab_token = "The kernelCI backend lab token"

Example file: lab-mylab.cfg
`
[default]
backend_fqdn = http(s)://api.mylab.com
lab_name = lab-mylab
lab_token = 123g5789-45f4-4f21-a485-7412589df235
`
