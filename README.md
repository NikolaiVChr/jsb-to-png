# jsb-to-png v1.05
Takes a JSBSim xml file as input and converts all the tables to PNG images

Requires python with plotly.express and plotly.graph_objects libraries.

A folder will be created in working folder named same as filename

In this folder PNG of the tables will be output, it *will* overwrite if the folder is not empty.

Each table in the JSB input file that you want to graph *MUST* have name="mytable" attribute in the `<table>` tag. That name will also be used a Y-axis title in the graphs.

For 2D and 3D tables `<independentVar>` tags *MUST* all have lookup= attributes

For 2D and 3D tables it will graph both a lines and a carpet plot

**Commandline:** python jsb-to-png.py [filename]

If no filename is specified in as commandline arg then "jsb-test.xml" is assumed.