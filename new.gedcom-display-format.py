#!/usr/bin/python3

"""
Convert a genealogy gedcom file into a format for display in
a network visualization too.

This code is released under the MIT License: https://opensource.org/licenses/MIT
Copyright (c) 2022 John A. Andrea
v1.0.0

No support provided.
"""

import sys
import re
import argparse
import readgedcom


# these colors for GraphML
NAME_COLOR = 'olive'
UNION_COLOR = 'lightsalmon'
PARENT_CONNECT = 'black'
CHILD_CONNECT = 'orange'
UNION_LABEL = '@'


def get_program_options():
    results = dict()

    results['format'] = 'graphml'
    results['infile'] = None
    results['include'] = 'all'
    results['personid'] = None
    results['iditem'] = 'xref'

    arg_help = 'Convert gedcom to network graph format.'
    parser = argparse.ArgumentParser( description=arg_help )

    formats = [results['format'], 'dot']
    arg_help = 'Output format. One of: ' + str(formats) + ', Default: ' + results['format']
    parser.add_argument( '--format', default=formats, choices=formats, type=str, help=arg_help )

    includes = [results['include'], 'ancestors', 'anc', 'descendents', 'desc', 'branch' ]
    arg_help = 'People to include. Default: ' + results['include']
    arg_help += ' An id for a person is required when not choosing ' + results['include']
    parser.add_argument( '--include', default=results['include'], choices=includes, type=str, help=arg_help )

    # if selecting ancestors or descendants, then the id of the selected persom
    # must be included
    # and it may be keyed off of the gedcom id or some other field such as exid or refid, etc

    arg_help = 'Id for the person chosen for ancestors or descendents.'
    parser.add_argument( '--personid', type=str, help=arg_help )

    arg_help = 'How to find the person. Default is the gedcom id "xref".'
    arg_help += ' Othewise choose "exid", "refnum", etc.'
    parser.add_argument( '--iditem', default=results['iditem'], type=str, help=arg_help )

    parser.add_argument('infile', type=argparse.FileType('r') )

    args = parser.parse_args()

    results['format'] = args.format.lower()
    results['include'] = args.include.lower()
    results['personid'] = args.personid
    results['iditem'] = args.iditem.lower()
    results['infile'] = args.infile.name

    return results


def get_name( individual, style ):
    # ouput formats deal with text in different "styles" for non-ascii characters
    # GraphML can dispay HTML
    # Dot can display ? fix this

    result = individual['name'][0][style]
    if readgedcom.UNKNOWN_NAME in result:
       result = 'unknown'
    else:
       # remove any suffix after the end slash
       result = re.sub( r'/[^/]*$', '', result ).replace('/','').strip()
    return result


def get_name_graphml( individual ):
    return get_name( individual, 'html' )


def get_name_dot( individual ):
    return get_name( individual, 'html' )  #fix this


def find_other_partner( indi, fam ):
    result = None

    other_partners = dict()
    other_partners['husb'] = 'wife'
    other_partners['wife'] = 'husb'

    other = None
    for partner in other_partners:
        if partner in data[fkey][fam]:
           if indi == data[fkey][fam][partner][0]:
              other = other_partners[partner]
              break

    if other:
       if other in data[fkey][fam]:
          result = data[fkey][fam][other][0]

    return result


def graphml_header():
    print( """\
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
        http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
""" )


def graphml_trailer():
    print( '</graphml>' )


def graphml_setup():
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


def begin_graphml():
    print( '<graph id="G" edgedefault="undirected">' )


def end_graphml():
    print( '</graph>' )


def graphml_node( n, color, name ):
    print( '<node id="n' + str(n) + '">' )
    print( '  <data key="d0">' + name + '</data>' )
    print( '  <data key="d1">' + color + '</data>' )
    print( '</node>' )


def graphml_names( n, node_match ):
    for indi in data[ikey]:
        name = get_name_graphml( data[ikey][indi] )
        node_match[indi] = n
        graphml_node( n, NAME_COLOR, name )
        n += 1
    return n


def graphml_unions( n, node_match ):
    for fam in data[fkey]:
        node_match[fam] = n
        # potentially a marriage date could be used as the label
        graphml_node( n, UNION_COLOR, UNION_LABEL )
        n += 1
    return n


def graphml_edge( n, s, t, color ):
    e = 'e' + str(n)
    s = 'n' + str(s)
    t = 'n' + str(t)
    print( '<edge id="' +e+ '" source="' +s+ '" target="' +t+ '">' )
    if color:
       print( '  <data key="d2">' + color + '</data>' )
    print( '</edge>' )


def graphml_connectors( indi_match, fam_match ):
    # only the children get a colored connector,
    # the parents use the default
    n = 0
    for fam in data[fkey]:
        target = fam_match[fam]
        for child in data[fkey][fam]['chil']:
            source = indi_match[child]
            graphml_edge( n, source, target, CHILD_CONNECT )
            n += 1
        for parent in ['husb','wife']:
            if parent in data[fkey][fam]:
               source = indi_match[data[fkey][fam][parent][0]]
               graphml_edge( n, source, target, PARENT_CONNECT )
               n += 1


def dot_header():
    print( 'digraph family {' )


def dot_setup():
    print( 'node [shape=record];' )
    print( 'rankdir=LR;' )


def begin_dot():
    print( '' )


def end_dot():
    print( '' )


def dot_trailer():
    print( '}' )


def make_dot_itag( n ):
    return 'i' + str( n )


def make_dot_ftag( n ):
    return 'f' + str( n )


def dot_singles( n, match_nodes ):
    # people with no partnerships
    for indi in the_individuals:
        if 'fams' not in data[ikey][indi]:
           n += 1
           match_nodes[indi] = n

           out = make_dot_itag(n) + ' [label="'
           out += '<i>' + get_name_dot( data[ikey][indi] )
           out += '"];'
           print( out )
    return n


def dot_unions( n, indi_nodes, fam_nodes ):
    # draw the partnerships in which each individual exists
    for indi in the_individuals:
        if 'fams' in data[ikey][indi]:
           for fam in data[ikey][indi]['fams']:
               if fam in the_families:
                  # skip if the family was drawn via the other partner
                  if fam in fam_nodes:
                     # still need to track this partner
                     if indi not in indi_nodes:
                        n += 1
                        indi_nodes[indi] = n
                  else:
                     n += 1
                     fam_nodes[fam] = n
                     fam_tag = make_dot_ftag( n )

                     names = dict()
                     for partner in ['wife','husb']:
                         if partner in data[fkey][fam]:
                            partner_id = data[fkey][fam][partner][0]
                            names[partner] = get_name_dot( data[ikey][partner_id] )
                            n += 1
                            indi_nodes[indi] = n

                         else:
                            names[partner] = 'unknown'

                     out = fam_tag + ' [label="'
                     out += '<h>' + names['husb']
                     out += '|<u>|'  # potentially marriage date could go in here
                     out += '<w>' + names['wife']
                     out += '"];'
                     print( out )

    return n


def dot_connectors( indi_nodes, fam_nodes ):
    # connections from people to their parent unions
    for indi in the_individuals:
        if 'famc' in data[ikey][indi]:
           child_of = data[ikey][indi]['famc'][0]
           if child_of in the_families:
              f_link = make_dot_ftag( fam_nodes[child_of] ) + ':p'

              # the tag for the individual depends on if its in a family or not
              if 'fams' in data[ikey][indi]:
                 # the connector will go from one of the families for this person
                 fam = data[ikey][indi]['fams'][0]

                 partner_key = 'h'
                 # but see if its the wife side of the structure
                 if 'wife' in data[fkey][fam]:
                    if indi == data[fkey][fam]['wife'][0]:
                       partner_key = 'w'

                 i_link = make_dot_ftag( fam_nodes[fam] ) + ':' + partner_key

              else:
                 i_link = make_dot_itag( indi_nodes[indi] ) + ':i'

              print( i_link + ' -> ' + f_link + ';' )


def find_person( person, item ):
    result = None

    if item == 'xref':
       # ensure the person lookup is the same as what it used in gedcom
       # if given  5  change to  @I5@
       person = 'i' + person.lower()
       person = '@' + person.replace( 'ii', 'i' ) + '@'
       person = person.replace( '@@', '@' )

       for indi in data[ikey]:
           rec_no = data[ikey][indi]['file_record']['index']
           rec_key = data[ikey][indi]['file_record']['key']
           if person == data[rec_key][rec_no]['tag'].lower():
              result = indi
              break

    else:
       for indi in data[ikey]:
           if item in data[ikey][indi]:
              if person == data[ikey][indi][item]:
                 result = indi
                 break

    return result


def add_ancestors( indi ):
    global the_individuals
    global the_families

    if 'famc' in data[ikey][indi]:
        fam = data[ikey][indi]['famc'][0]
        if fam not in the_families:
           the_families.append( fam )
        for partner in ['wife','husb']:
            if partner in data[fkey][fam]:
               parent_id = data[fkey][fam][partner][0]
               if parent_id not in the_individuals:
                  the_individuals.append( parent_id )
                  add_ancestors( parent_id )


def add_descendents( indi ):
    global the_individuals
    global the_families

    if 'fams' in data[ikey][indi]:
       for fam in data[ikey][indi]['fams']:
           if fam not in the_families:
              the_families.append( fam )
           if 'chil' in data[fkey][fam]:
              for child in data[fkey][fam]['chil']:
                  if child not in the_individuals:
                     the_individuals.append( child )
                     add_descendents( child )
           # need to also add the partner in this family
           # so that the family will be displayed
           # but do not travel down this person's descendents
           other = find_other_partner( indi, fam )
           if other is not None:
              the_individuals.append( other )


def get_individuals( who_to_include, person_id, id_item ):
    global the_individuals
    global the_families

    result = True

    if who_to_include == 'all':
       for indi in data[ikey]:
           the_individuals.append( indi )
       for fam in data[fkey]:
           the_families.append( fam )

    else:
       if person_id is None:
          print( 'The id of a person is required for branch selection.', file=sys.stderr )
          result = False
       else:

          person_indi = find_person( person_id, id_item )

          if person_indi is not None:

             print( 'Selected person', person_indi, '=', get_name(data[ikey][person_indi], 'html'), file=sys.stderr )
             the_individuals.append( person_indi )

             if who_to_include in ['ancestors','anc']:
                print( 'Output ancestors', file=sys.stderr )
                add_ancestors( person_indi )

             elif who_to_include in ['descendents','desc']:
                print( 'Output descendents', file=sys.stderr )
                add_descendents( person_indi )

             elif who_to_include == 'branch':
                print( 'Output ancestors and descendents', file=sys.stderr )
                add_ancestors( person_indi )
                add_descendents( person_indi )

             else:
                print( 'Unknown option for include:', who_to_include, file=sys.stderr )
                result = False

          else:
             print( 'Did not locate specified person', person_id, 'in', id_item, file=sys.stderr )
             result = False

    return result


def output_data( out_format ):
    result = True

    # put each person into a node
    # and each family also
    n_nodes = 0

    # by creating a new list
    indi_nodes = dict()
    fam_nodes = dict()

    if out_format == 'graphml':
       graphml_header()
       graphml_setup()
       begin_graphml()

       n_nodes = graphml_names( n_nodes, indi_nodes )
       n_nodes = graphml_unions( n_nodes, fam_nodes )
       graphml_connectors( indi_nodes, fam_nodes )

       end_graphml()
       graphml_trailer()

    elif out_format == 'dot':
       dot_header()
       dot_setup()
       begin_dot()

       n_nodes = dot_unions( n_nodes, indi_nodes, fam_nodes )
       n_nodes = dot_singles( n_nodes, indi_nodes )
       dot_connectors( indi_nodes, fam_nodes )

       end_dot()
       dot_trailer()

    else:
       print( 'Unknown format', out_format, file=sys.stderr )
       result = False

    return result


options = get_program_options()

ikey = readgedcom.PARSED_INDI
fkey = readgedcom.PARSED_FAM

data = readgedcom.read_file( options['infile'] )

# find the people that should be output
the_individuals = []
the_families = []

exit_code = 1

if ikey in data:

   if get_individuals( options['include'], options['personid'], options['iditem'] ):

      #print( 'individuals', file=sys.stderr ) #debug
      #for i in the_individuals:
      #    print( i, get_name( data[ikey][i], 'html') , file=sys.stderr ) #debug

      if output_data( options['format'] ):
         exit_code = 0

else:
   print( 'Data not correct format.', file=sys.stderr )

sys.exit( exit_code )
