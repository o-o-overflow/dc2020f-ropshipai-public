# ropshipai DEFCON 2020 Finals

This challenge contains the challenge `ropshipai` prepared for `DEFCON 2020 Finals`.
## How to run
`./start.sh simulated`

The code assumes `python3` and a Linux environemnt.

It also requires the `shapely` Python package.

The code will run using, as teams' submitted solutions, the content of the folder `inputs`.

Once it finishes, you can see the resulting game by using the visualizer:

`./visualizer.py /dev/shm/ropship/states tmp/`

To compile generate teams' solutions, you can use `generate_inputs.py`.
This script supports, optionally, different command line arguments, to generate different solutions.

## Submitted data
The file `ropshipai_submitted.tgz.gpg` contains the solutions submitted by teams during `DEFCON 2020 Finals`.

**We do NOT have absoluty any responsability on the content of `ropshipai_submitted.tgz.gpg`**

**Most likely, it includes malicious code and data.**

The file is `gpg` encrypted using the following passphrase:

`IAmAwareThatThisFileMayContainMaliciousStuff2020`

