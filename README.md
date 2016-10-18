# jiggle_jenkins
Jiggle the knobs on a Jenkins server to get bummed out builds unbummed


## Pre-requisites
* Python (tested on 3.5, may work on others)
* jenkinsapi ([https://github.com/pycontribs/jenkinsapi](https://github.com/pycontribs/jenkinsapi/))
* click ([http://click.pocoo.org/5/](http://click.pocoo.org/5/)]

jenkinsapi and click can be installed with pip.

## What does it do?
jiggle_jenkins.py simply queries the specified Jenkins server for all projects,
checking their last-build status. Projects which are enabled but have failed on
the last build will be queued for rebuild.

The need for such a script arose out of mass build failures which would occur, for
instance, when nightly jobs kicked off whilst the server's internet connection was
down. Basically, it's a Big Hammer to circumvent click fatigue.

## Usage
Running the script with `--help` should elucidate, thanks to the super-convenient
`click` library. When using authentication, jiggle_jenkins uses the `getpass` Python
library which attempts to find your username via environment variables and the like. If
you wish to authenticate with different credentials, use the `--user` argument and you
will still be prompted for a password. Use the `--password` argument if you don't want
a prompt (with the standard disclaimer that this obviously exposes your password)