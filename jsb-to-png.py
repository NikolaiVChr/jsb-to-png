# Function: JSBSim tables to PNG outputs
# Author: Nikolai V. Chr.
#
# License: GPL 2.0
#


import xml.dom.minidom
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys



filename="jsb-test.xml"
image_width = 1280
image_height = 720

#
# A folder will be created in working folder named same as filename
# In this folder PNG of the tables will be output
#
# Each table in the JSB input file that you want to graph MUST have name="mytable" attribute in the <table> tag
# For 2D and 3D tables <independentVar> tags MUST all have lookup= attribute
#
# For 2D and 3D tables it will graph both a lines and a carpet plot
#
# Commandline: python jsb-to-png.py [filename]
#
# If no filename is specified in as commandline arg then "jsb-test.xml" is assumed.


if len(sys.argv) > 1:
    filename = str(sys.argv[1])




file=os.path.splitext(filename)[0]

if not os.path.exists(os.getcwd()+"/"+file):
    os.mkdir(os.getcwd()+"/"+file)

print ("parsing "+filename)
doc=xml.dom.minidom.parse (filename)

tables=doc.getElementsByTagName("table")


def runner(line):
    numbs = line.strip().split()
    if len(numbs) < 2:
        return []
    return list(map(float, numbs))

for table in tables:
    name = table.getAttribute("name")
    if not name:
        continue
    name = name.replace('/','-')
    vars = table.getElementsByTagName("independentVar")

    if len(vars) == 1:
        var = vars[0].firstChild.data
        rawData = table.getElementsByTagName("tableData")[0].firstChild.data

        lines = rawData.split('\n')

        dx = []
        dy = []

        mapp = map(runner, lines)
        lineList = list(mapp)
        for xy in lineList:
            if len(xy) == 2:
                dx.append(xy[0])
                dy.append(xy[1])

        data = {var: dx, name: dy}

        fig = px.line(data, x=var, y=name)#, color=''
        fig.write_image(file+"/"+name+".png", format='png', width=image_width, height=image_height, scale=1)
    elif len(vars) == 2:
        row = ''
        column = ''
        if vars[0].getAttribute('lookup') == "row":
            row = vars[0].firstChild.data
            column = vars[1].firstChild.data
        elif vars[0].getAttribute('lookup') == "column":
            row = vars[1].firstChild.data
            column = vars[0].firstChild.data
        else:
            continue
        rawData = table.getElementsByTagName("tableData")[0].firstChild.data

        lines = rawData.split('\n')

        dx = []
        dy = None
        dz = []

        mapp = map(runner, lines)
        lineList = list(mapp)

        for xyz in lineList:
            if len(xyz) < 2:
                continue
            if not dy:
                dy = xyz
            else:
                dx.append(xyz[0])
                dz.append(np.array(xyz[1:]))
        dz = np.array(dz)
        fig = go.Figure(go.Carpet(
            a=dy,
            b=dx,
            y=dz,
            aaxis=dict(
                title=column
            ),
            baxis=dict(
                title=row
            )
        ), layout=dict(yaxis=dict(title=name)))

        fig.write_image(file+"/" + name + ".carpet.png", format='png', width=image_width, height=image_height, scale=1)

        fig2 = go.Figure()

        for num in range(len(dy)):
            data = dz[0:,num]
            fig2.add_trace(go.Scatter(x=dx, y=data, name=str(dy[num]), mode='lines'))
        fig2.update_layout(
            title="Color code from "+column,
            yaxis=dict(title=name),
            xaxis=dict(title=row),
        )
        fig2.write_image(file+"/" + name + ".png", format='png', width=image_width, height=image_height, scale=1)
    elif len(vars) == 3:
        row = ''
        column = ''
        breakpoint=''
        if vars[0].getAttribute('lookup') == "row":
            if vars[1].getAttribute('lookup') == "column":
                row = vars[0].firstChild.data
                column = vars[1].firstChild.data
                breakpoint = vars[2].firstChild.data
            elif vars[1].getAttribute('lookup') == "table":
                row = vars[0].firstChild.data
                column = vars[2].firstChild.data
                breakpoint = vars[1].firstChild.data
            else:
                continue
        elif vars[0].getAttribute('lookup') == "column":
            if vars[1].getAttribute('lookup') == "row":
                row = vars[1].firstChild.data
                column = vars[0].firstChild.data
                breakpoint = vars[2].firstChild.data
            elif vars[1].getAttribute('lookup') == "table":
                row = vars[2].firstChild.data
                column = vars[0].firstChild.data
                breakpoint = vars[1].firstChild.data
            else:
                continue
        elif vars[0].getAttribute('lookup') == "table":
            if vars[1].getAttribute('lookup') == "row":
                row = vars[1].firstChild.data
                column = vars[2].firstChild.data
                breakpoint = vars[0].firstChild.data
            elif vars[1].getAttribute('lookup') == "column":
                row = vars[2].firstChild.data
                column = vars[1].firstChild.data
                breakpoint = vars[0].firstChild.data
            else:
                continue
        else:
            continue

        for breakTable in table.getElementsByTagName("tableData"):
            rawData = breakTable.firstChild.data
            breakValue = breakTable.getAttribute("breakPoint")

            lines = rawData.split('\n')

            dx = []
            dy = None
            dz = []

            mapp = map(runner, lines)
            lineList = list(mapp)

            for xyz in lineList:
                if len(xyz) < 2:
                    continue
                if not dy:
                    dy = xyz
                else:
                    dx.append(xyz[0])
                    dz.append(np.array(xyz[1:]))
            dz = np.array(dz)
            fig = go.Figure(go.Carpet(
                a=dy,
                b=dx,
                y=dz,
                aaxis=dict(
                    title=column
                    #tickprefix=column + ':',
                    #ticksuffix='m',
                    #smoothing=1,
                    #minorgridcount=9,
                    #minorgridwidth=0.6,
                    #minorgridcolor='white',
                    #gridcolor='white',
                    #color='white'
                ),
                baxis=dict(
                    title=row
                    #tickprefix=row + ':',
                    #ticksuffix='Pa',
                    #smoothing=1,
                    #minorgridcount=9,
                    #minorgridwidth=0.6,
                    #gridcolor='white',
                    #minorgridcolor='white',
                    #color='white'
                )
            ), layout=dict(title="             "+breakpoint+" breakPoint="+str(breakValue),
                           yaxis = dict(title=name),))

            fig.write_image(file+"/" + name +str(breakValue)+ ".carpet.png", format='png', width=image_width, height=image_height, scale=1)

            fig2 = go.Figure()

            for num in range(len(dy)):
                data = dz[0:,num]
                fig2.add_trace(go.Scatter(x=dx, y=data, name=str(dy[num]), mode='lines'))
            fig2.update_layout(
                title="Breakpoint "+breakpoint+"="+str(breakValue)+",    Color code from "+column,
                yaxis=dict(title=name),
                xaxis=dict(title=row),
            )
            fig2.write_image(file+"/" + name +str(breakValue)+ ".png", format='png', width=image_width, height=image_height, scale=1)