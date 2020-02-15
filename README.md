# Welcome to the GIMME project repository

<img src="ReadmeImages/logo.png" width="300">


GIMME (Group Interactions Management for Multiplayer sErious games) is a research tool which focuses on the management of 
interactions in groups so that the collective ability improves. 
More specifically, what sets the method appart is that the interactions between players are explicity considered when forming group configurations (also called coalition structures in some problems).
This repository contains the core of the application (written in Python), as well as some examples. 
Over time, we aim to improve the core functionalities as well as provide more examples for GIMME.


## Requirements

GIMME only requires Python 3 in order to be executed (Tested in Python 3.7.4). No additional tools are required.
Tested on Windows and Linux. May also work in MacOS.


## Setup

GIMME setup is straightforward. You just got to install the python package:

```python 
python3 setup.py install
```

Then you can start to write programs with our library.
When importing the package, it is recommended to use the following command:

```python 
from GIMMECore import *
```
This will automatically import all of the associated GIMME classes.


## Run an example

Some simulations are provided as example use cases of our system. To execute the provided simulations, you just have to enter the folder examples and call python as usual:

```python 
cd examples
python simulations.py
```

## More Information
Additional information about the API internals and examples can be observed in our [wiki](https://github.com/SamGomes/GIMME/wiki).

## License
The current and previous versions of the code are licensed according to Attribution 4.0 International (CC BY 4.0).  
 
 <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />
