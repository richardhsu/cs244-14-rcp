# Rate Control Protocol (RCP)

This project was done for CS 244 Spring 2014 by Lisa Yan and Richard Hsu. The project includes simulation code used to reproduce the RCP work results of the Average Completion Time for varying Flow Sizes (See Figure 12 of the [full paper][full]).

## Rate Control Protocol

"Why Flow-Completion Time is the Right Metric for Congestion Control" [\[pdf\]][paper] [\[full version\]][full]
by Nandita Dukkipati and Nick McKeown (http://yuba.stanford.edu/rcp/)

## Reproduction Setup

### Amazon EC2 AMI

We provide an easy Amazon EC2 AMI for you to run the simulation test code. It has everything set up so you only need to run the code and view the output! On Amazon EC2 in the Oregon location the AMI's name is "**FILL OUT**" and the ID is `FILL OUT`.

### Your Own Setup

The following are instructions to help you run it on your own system. We cannot guarantee it will work for all systems but this has been tested on Ubuntu 14.04 LTS.

#### Installing NS-2.35 with RCP code

You will need to install NS-2.35 All In One package on your system, which you can place anywhere on your system.

**Step 0**: You'll want to make sure you have the necessary tools installed. The following can be used for Ubuntu systems and have been tested for Ubuntu 14.04 LTS. Generally speaking you'll need tools for building, autoconf, g++/gcc and X11 library code.

```bash
sudo apt-get install build-essential autoconf automake perl g++ libx11-dev libxt-dev libx11-dev libxmu-dev
```

**Step 1**: In the folder that you want NS-2.35 code perform the following steps:

```bash
wget http://downloads.sourceforge.net/project/nsnam/allinone/ns-allinone-2.35/ns-allinone-2.35.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fnsnam%2Ffiles%2Fallinone%2Fns-allinone-2.35%2F&ts=1401492260&use_mirror=tcpdiag -O ns-allinone-2.35.tar.gz
tar -xzvf ns-allinone-2.35.tar.gz
```

**Step 2:**: Next you'll want to patch it for RCP. Copy the `rcp-2.35.patch` file from our repository into the `ns-allinone-2.35` directory. Next you'll perform the patch:

```bash
patch -p1 < rcp-2.35.patch
```

**Step 3:** Now you'll want to install the whole NS package and dependencies. In the top level of the `ns-allinone-2.35` folder run the install command:

```bash
./install
```

Hopefully it will install successfully, if not read the error codes and fix. Unforutnately we may not be able to provide assistance with this.

**Step 4:** The installation should provide some output on changing the path. You should follow those instructions but here it is reproduced assuming the path to `ns-allinone-2.35` is `/home/ubuntu/ns-allinone-2.35`:

```
Please put /home/ubuntu/ns-allinone-2.35/bin:/home/ubuntu/ns-allinone-2.35/tcl8.5.10/unix:/home/ubuntu/ns-allinone-2.35/tk8.5.10/unix
into your PATH environment; so that you'll be able to run itm/tclsh/wish/xgraph.

IMPORTANT NOTICES:

(1) You MUST put /home/ubuntu/ns-allinone-2.35/otcl-1.14, /home/ubuntu/ns-allinone-2.35/lib,
    into your LD_LIBRARY_PATH environment variable.
    If it complains about X libraries, add path to your X libraries
    into LD_LIBRARY_PATH.
    If you are using csh, you can set it like:
                setenv LD_LIBRARY_PATH <paths>
    If you are using sh, you can set it like:
                export LD_LIBRARY_PATH=<paths>

(2) You MUST put /home/ubuntu/ns-allinone-2.35/tcl8.5.10/library into your TCL_LIBRARY environmental
    variable. Otherwise ns/nam will complain during startup.
```

**Step 5:** Install NS-2.35 as well so it can be executed on the command line:

```
cd ns-2.35
./configure
make clean
make
make install
```

The last line may require a `sudo make install` instead depending on permissions.

#### Matplotlib, SciPy, NumPy

Our graphing script and PS analysis require `matplotlib` and `scipy` for Python in order to generate the graphs. You can install it on Ubuntu as follows:

```bash
sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
```

Otherwise for other Linux systems, make sure to find out how to install it. Refer to the respective software sites for more information.

## Reproduction Code

Now you just need to go into the `simulation` folder of our code and type `./run.sh`. You may need execution permissions if it isn't set properly when you've cloned the repository. You'll find the graphs produced and you can read about our reproduction of the research results [here][wordpress].

[paper]: http://yuba.stanford.edu/rcp/flowCompTime-dukkipati.pdf
[full]: http://yuba.stanford.edu/techreports/TR05-HPNG-112102.pdf
[wordpress]: http://www.wordpress.org

