# jsb-to-png v1.07
Takes a JSBSim xml file as input and converts all the tables to PNG images

Requires python with plotly.express and plotly.graph_objects libraries.

A folder will be created in working folder named same as the jsb input filename, but without the xml extension.

In that folder PNG of the tables will be output, it *will* overwrite images if the folder is not empty.

Each table in the JSB input file that you want to graph *MUST* have name="mytable" attribute in the `<table>` tag. That name will also be used a Y-axis title in the graphs. Do not have multiple tables with same name since its used in naming the image files also.

For 2D and 3D tables `<independentVar>` tags *MUST* all have lookup= attributes

For 2D and 3D tables it will graph both a lines and a carpet plot

**Commandline:** python jsb-to-png.py [filename]

If no filename is specified in as commandline arg then "jsb-test.xml" is assumed.

Example output:

![image](https://i.postimg.cc/kXRvj106/Cm-de0-0.png)