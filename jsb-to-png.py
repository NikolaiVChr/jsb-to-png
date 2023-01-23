#!/usr/bin/env python3
#
# Function: JSBSim tables to PNG outputs
# Author: Nikolai V. Chr.
#
# License: GPL 2.0
#
# See more info in the readme and license files
#
import xml.dom.minidom
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys
#import re

version = "1.09"

# default filename
filename="jsb-test.xml"

# default PNG output image size
image_width = 1280
image_height = 720

print("Starting JSBSim to PNG program, version "+version)

if len(sys.argv) > 1:
    filename = str(sys.argv[1])

file=os.path.splitext(filename)[0]

print ("Parsing "+filename)
doc=xml.dom.minidom.parse (filename)


if not os.path.exists(os.getcwd()+os.sep+file):
    print("Making folder " + os.getcwd() + os.sep + file)
    os.mkdir(os.getcwd()+os.sep+file)
else:
    print("Output to folder " + os.getcwd() + os.sep + file + " (will overwrite PNG images if exist)")

tables=doc.getElementsByTagName("table")


def runner(line):
    numbs = line.strip().split()
    if len(numbs) < 2:
        return []
    return list(map(float, numbs))

print("Generating the ("+str(image_width)+"x"+str(image_height)+") PNG images..")
tablecount = 0
ignorecount = 0
ignored = []
current = 0

for table in tables:
    current += 1
    name = table.getAttribute("name")
    if not name:
        ignorecount += 1
        ignored.append(current)
        continue
    name = name.replace('/','-')
    vars = table.getElementsByTagName("independentVar")

    if len(vars) == 1:
        var = vars[0].firstChild.data
        rawData = table.getElementsByTagName("tableData")[0]
        rawData = " ".join(t.nodeValue for t in rawData.childNodes if t.nodeType == t.TEXT_NODE)
        #rawData = re.sub("(<!--.*?-->)", "", rawData, flags=re.DOTALL)

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
        tablecount += 1
        fig.write_image(file+os.sep+name+".png", format='png', width=image_width, height=image_height, scale=1)
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
            ignorecount += 1
            continue
        rawData = table.getElementsByTagName("tableData")[0]
        rawData = " ".join(t.nodeValue for t in rawData.childNodes if t.nodeType == t.TEXT_NODE)
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
                title=column,
                color = 'blue',
                linecolor='blue',
                gridcolor='lightblue'
            ),
            baxis=dict(
                title=row,
                gridcolor='lightgreen'
            )
        ), layout=dict(yaxis=dict(title=name)))

        fig.write_image(file+os.sep + name + ".carpet.png", format='png', width=image_width, height=image_height, scale=1)

        fig2 = go.Figure()

        for num in range(len(dy)):
            data = dz[0:,num]
            fig2.add_trace(go.Scatter(x=dx, y=data, name=str(dy[num]), mode='lines'))
        fig2.update_layout(
            #title="Color code from "+column,
            yaxis=dict(title=name),
            xaxis=dict(title=row),
            legend_title=dict(text=column)
        )
        fig2.write_image(file+os.sep + name + ".png", format='png', width=image_width, height=image_height, scale=1)
        tablecount += 1
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
                ignorecount += 1
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
                ignorecount += 1
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
                ignorecount += 1
                continue
        else:
            ignorecount += 1
            continue

        for breakTable in table.getElementsByTagName("tableData"):
            rawData = " ".join(t.nodeValue for t in breakTable.childNodes if t.nodeType == t.TEXT_NODE)
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
                    title=column,
                    color = 'blue',
                    linecolor = 'blue',
                    #tickprefix=column + ':',
                    #ticksuffix='m',
                    #smoothing=1,
                    #minorgridcount=9,
                    #minorgridwidth=0.6,
                    #minorgridcolor='white',
                    gridcolor='lightblue'
                    #color='white'
                ),
                baxis=dict(
                    title=row,
                    gridcolor='lightgreen'
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

            fig.write_image(file+os.sep + name +str(breakValue)+ ".carpet.png", format='png', width=image_width, height=image_height, scale=1)

            fig2 = go.Figure()

            for num in range(len(dy)):
                data = dz[0:,num]
                fig2.add_trace(go.Scatter(x=dx, y=data, name=str(dy[num]), mode='lines'))
            fig2.update_layout(
                title="Breakpoint "+breakpoint+"="+str(breakValue),#+",    Color code from "+column,
                yaxis=dict(title=name),
                xaxis=dict(title=row),
                legend_title=dict(text=column)#,
                                                 #    font=dict(family="sans-serif",
                                                 #              size=18,
                                                 #              color='blue')
            )
            fig2.write_image(file+ os.sep + name +str(breakValue)+ ".png", format='png', width=image_width, height=image_height, scale=1)
            tablecount += 1


print("Finished. Successfully processed "+str(tablecount)+" tables.")
if ignorecount > 0:
    print("Ignored "+str(ignorecount)+" table(s) (see readme on how to avoid tables being ignored).")
    print("Ignored table(s) number: ", ignored)
