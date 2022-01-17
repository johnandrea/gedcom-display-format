#!/usr/bin/python3

"""
Convert a genealogy gedcom file into a format for display in
a network visualization too.

This code is released under the MIT License: https://opensource.org/licenses/MIT
Copyright (c) 2022 John A. Andrea
v0.0.0

No support provided.
"""

import sys
import readgedcom

def output_header():
    print( """\
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns 
        http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
""" )


def output_trailer():
    print( '</graphml>' )


def output_setup():
    print( """\
<key id="d0" for="node" attr.name="name" attr.type="string">
  <default>@</default>
</key>
<key id="d1" for="node" attr.name="color" attr.type="string">
  <default>green</default>
</key>
<key id="d2" for="edge" attr.name="color" attr.type="string">
  <default>orange</default>
</key>
""" )


def begin_graph():
    print( '<graph id="G" edgedefault="undirected">' )


def end_graph():
    print( '</graph>' )


def output_node( n, color, name ):
    print( '<node id="n' + str(n) + '">' )
    print( '  <data key="d0">' + name + '</data>' )
    print( '  <data key="d1">' + color + '</data>' )
    print( '</node>' )


def output_names( n, color, node_match ):
    for indi in data[ikey]:
        name = str( indi ) #for now
        node_match[indi] = n
        output_node( n, color, name )
        n += 1
    return n


def output_unions( n, color, node_match ):
    for fam in data[fkey]:
        node_match[fam] = n
        output_node( n, color, '@' )
        n += 1
    return n


def output_edge( n, s, t, color ):
    e = 'e' + str(n)
    s = 'n' + str(s)
    t = 'n' + str(t)
    print( '<edge id="' +e+ '" source="' +s+ '" target="' +t+ '">' )
    if color:
       print( '  <data key="d2">' + color + '</data>' )
    print( '</edge>' )


def output_connectors( parent_color, child_color, indi_match, fam_match ):
    # only the children get a colored connector,
    # the parents use the default
    n = 0
    for fam in data[fkey]:
        target = fam_match[fam]
        for child in data[fkey][fam]['chil']:
            source = indi_match[child]
            output_edge( n, source, target, child_color )
            n += 1
        for parent in ['husb','wife']:
            if parent in data[fkey][fam]:
               source = indi_match[data[fkey][fam][parent][0]]
               output_edge( n, source, target, parent_color )
               n += 1


ikey = readgedcom.PARSED_INDI
fkey = readgedcom.PARSED_FAM

data = readgedcom.read_file( sys.argv[1] )

# put each person into a node
# and each family also
n_nodes = 0

# by creating a new list
indi_nodes = dict()
fam_nodes = dict()

output_header()
output_setup()
begin_graph()

n_nodes = output_names( n_nodes, 'olive', indi_nodes )
n_nodes = output_unions( n_nodes, 'lightsalmon', fam_nodes )
output_connectors( 'grey', 'orange', indi_nodes, fam_nodes )

end_graph()
output_trailer()