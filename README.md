# jsb-to-png
Takes a JSBSim xml file as input and converts all the tables to PNG images

Requires python with plotly.express and plotly.graph_objects libraries.

A folder will be created in working folder named same as filename

In this folder PNG of the tables will be output

Each table in the JSB input file that you want to graph *MUST* have name="mytable" attribute in the `<table>` tag

For 2D and 3D tables `<independentVar>` tags *MUST* all have lookup= attributes

For 2D and 3D tables it will graph both a lines and a carpet plot