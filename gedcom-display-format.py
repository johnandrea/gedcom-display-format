#!/usr/bin/python3

"""
Convert a genealogy gedcom file into a format for display in
a network visualization too.

This code is released under the MIT License: https://opensource.org/licenses/MIT
Copyright (c) 2022 John A. Andrea

No support provided.
"""

import sys
import re
import argparse
import json
import importlib.util
import os


# these colors for GraphML
NAME_COLOR = 'olive'
UNION_COLOR = 'lightsalmon'
PARENT_CONNECT = 'black'
CHILD_CONNECT = 'orange'
UNION_LABEL = '@'


def get_version():
    return '3.0'


def load_my_module( module_name, relative_path ):
    """
    Load a module in my own single .py file. Requires Python 3.6+
    Give the name of the module, not the file name.
    Give the path to the module relative to the calling program.
    Requires:
        import importlib.util
        import os
    Use like this:
        readgedcom = load_my_module( 'readgedcom', '../libs' )
        data = readgedcom.read_file( input-file )
    """
    assert isinstance( module_name, str ), 'Non-string passed as module name'
    assert isinstance( relative_path, str ), 'Non-string passed as relative path'

    file_path = os.path.dirname( os.path.realpath( __file__ ) )
    file_path += os.path.sep + relative_path
    file_path += os.path.sep + module_name + '.py'

    assert os.path.isfile( file_path ), 'Module file not found at ' + str(file_path)

    module_spec = importlib.util.spec_from_file_location( module_name, file_path )
    my_module = importlib.util.module_from_spec( module_spec )
    module_spec.loader.exec_module( my_module )

    return my_module


def get_program_options():
    results = dict()

    results['format'] = 'graphml'
    results['infile'] = None
    results['include'] = 'all'
    results['personid'] = None
    results['iditem'] = 'xref'
    results['dates'] = False
    results['reverse'] = False
    results['thick'] = 1
    results['libpath'] = '.'

    arg_help = 'Convert gedcom to network graph format.'
    parser = argparse.ArgumentParser( description=arg_help )

    arg_help = 'Show version then exit.'
    parser.add_argument( '--version', action='version', version=get_version() )

    formats = [results['format'], 'dot', 'json', 'dot2']
    arg_help = 'Output format. One of: ' + str(formats) + ', Default: ' + results['format']
    parser.add_argument( '--format', default=formats, choices=formats, type=str, help=arg_help )

    includes = [results['include'], 'ancestors', 'anc', 'descendents', 'desc', 'branch', 'br' ]
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

    arg_help = 'Show dates along with the names.'
    parser.add_argument( '--dates', default=results['dates'], action='store_true', help=arg_help )

    # in dot files, change direction of the arrows
    arg_help = 'For dot file output, reverse the order of the links.'
    parser.add_argument( '--reverse', default=results['reverse'], action='store_true', help=arg_help )

    # this option can be repeated for extra thickness
    arg_help = 'Increase width of connecting lines'
    parser.add_argument( '--thick', action='count', help=arg_help )

    # maybe this should be changed to have a type which better matched a directory
    arg_help = 'Location of the gedcom library. Default is current directory.'
    parser.add_argument( '--libpath', default=results['libpath'], type=str, help=arg_help )

    parser.add_argument('infile', type=argparse.FileType('r') )

    args = parser.parse_args()

    results['format'] = args.format.lower()
    results['include'] = args.include.lower()
    results['personid'] = args.personid
    results['iditem'] = args.iditem.lower()
    results['dates'] = args.dates
    results['infile'] = args.infile.name
    results['reverse'] = args.reverse
    results['libpath'] = args.libpath

    value = args.thick
    if value:
       results['thick'] += value

    # change to full words
    key = 'include'
    if results[key] in ['anc']:
       results[key] = 'ancestors'
    if results[key] in ['desc']:
       results[key] = 'descendents'
    if results[key] in ['br']:
       results[key] = 'branch'

    return results


def get_indi_years( indi ):
    # return ( birth - death ) or (birth-) or (-death)
    # but None if both dates are empty

    def get_indi_year( indi_data, tag ):
        # "best" year for birth, death, ...
        # or an empty string
        result = ''

        best = 0
        if readgedcom.BEST_EVENT_KEY in indi_data:
           if tag in indi_data[readgedcom.BEST_EVENT_KEY]:
              best = indi_data[readgedcom.BEST_EVENT_KEY][tag]
        if tag in indi_data:
           if indi_data[tag][best]['date']['is_known']:
              result = str( indi_data[tag][best]['date']['min']['year'] )
        return result

    result = None

    birth = get_indi_year( data[ikey][indi], 'birt' ).strip()
    death = get_indi_year( data[ikey][indi], 'deat' ).strip()
    if birth or death:
       result = '(' + birth +'-'+ death + ')'

    return result


def get_name( indi, style, line_break=' ' ):
    # ouput formats deal with text in different "styles" for non-ascii characters
    # GraphML can dispay HTML encodings.
    # Dot can also display HTML.

    result = 'none'

    if indi is not None:
       result = data[ikey][indi]['name'][0][style]
       if readgedcom.UNKNOWN_NAME in result:
          # change to word with no special characters
          result = 'unknown'
       else:
          # remove any suffix after the end slash
          result = re.sub( r'/[^/]*$', '', result ).replace('/','').strip()

          if style == 'html':
             # escape quotes
             result = result.replace('"','&quot;').replace("'","&rsquo;")

          if options['dates']:
             dates = get_indi_years( indi )
             if dates:
                result += line_break + dates

    return result


def get_name_graphml( indi ):
    # not s string to repersent newline (\\n) but an actual newline (\n)
    return get_name( indi, 'html', '\n' )


def get_name_dot( indi ):
    return get_name( indi, 'html', '\\n' )


def get_name_json( indi ):
    # dates in the json ought to be handled as a separate key,
    # but that breaks this flow
    return get_name( indi, 'html', ' ' )


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
    #print( '<graph id="G" edgedefault="undirected">' )
    print( '<graph id="G" edgedefault="directed">' )


def end_graphml():
    print( '</graph>' )


def graphml_node( n, color, name ):
    print( '<node id="n' + str(n) + '">' )
    print( '  <data key="d0">' + name + '</data>' )
    print( '  <data key="d1">' + color + '</data>' )
    print( '</node>' )


def graphml_names( n, node_match ):
    for indi in the_individuals:
        name = get_name_graphml( indi )
        node_match[indi] = n
        graphml_node( n, NAME_COLOR, name )
        n += 1
    return n


def graphml_unions( n, node_match ):
    for fam in the_families:
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
    n = 0
    for fam in the_families:
        fam_target = fam_match[fam]
        for child in data[fkey][fam]['chil']:
            if child in the_individuals:
               child_target = indi_match[child]
               n += 1
               # the child it the target
               graphml_edge( n, fam_target, child_target, CHILD_CONNECT )
        for parent in ['husb','wife']:
            if parent in data[fkey][fam]:
               parent_id = data[fkey][fam][parent][0]
               if parent_id in the_individuals:
                  source = indi_match[parent_id]
                  n += 1
                  # the union node is the target
                  graphml_edge( n, source, fam_target, PARENT_CONNECT )


def dot_header():
    print( 'digraph family {' )


def dot_setup( thickness ):
    print( 'node [shape=record];' )
    print( 'edge [penwidth=' + str( thickness ) + '];' )
    print( 'rankdir=LR;' )


def dot_trailer():
    print( '}' )


def make_dot_itag( n ):
    return 'i' + str( n )


def make_dot_ftag( n ):
    return 'f' + str( n )


def dot_families( style2, n, indi_nodes, fam_nodes ):
    for fam in the_families:
        if fam not in fam_nodes:

           n += 1
           fam_tag = make_dot_ftag( n )

           # 'u' matches center of family structure
           fam_nodes[fam] = { 'tag':fam_tag, 'key':'u' }

           names = dict()
           names['wife'] = '?'
           names['husb'] = '?'

           for partner in names:
               if partner in data[fkey][fam]:
                  person_id = data[fkey][fam][partner][0]
                  # first char of partner matches 'h' and 'w' in structure
                  fam_key = partner[0:1]
                  if style2:
                     # for this style, no separate parents
                     fam_key = 'u'
                  indi_nodes[person_id] = { 'tag':fam_tag, 'key':fam_key }
                  names[partner] = get_name_dot( person_id )

           out = fam_tag + ' [label="'
           if style2:
              # both parents together, helps with reducing line crossing
              out += '<u>' + names['husb']
              out += '\\n& ' + names['wife']
           else:
              out += '<h>' + names['husb']
              out += '|<u>|'  # potentially marriage date could go in here
              out += '<w>' + names['wife']
           out += '"];'
           print( out )

    return n


def dot_not_families( n, indi_nodes ):
    # not a parent or spouse
    for indi in the_individuals:
        if indi not in indi_nodes:
           # and the person is not in any of the families which are selected
           in_a_fam = False
           item = 'fams'
           if item in data[ikey][indi]:
              for fam in data[ikey][indi][item]:
                  if fam in the_families:
                     in_a_fam = True
                     break
           if not in_a_fam:
              n += 1
              tag = make_dot_itag(n)
              # 'i' matches structure
              indi_nodes[indi] = { 'tag':tag, 'key':'i' }

              out = tag + ' [label="'
              out += '<i>' + get_name_dot( indi )
              out += '"];'
              print( out )

    return n


def dot_connectors( indi_nodes, fam_nodes, reverse_links ):
    # connections from people to their parent unions
    for indi in the_individuals:
        if 'famc' in data[ikey][indi]:
           child_of = data[ikey][indi]['famc'][0]
           if child_of in the_families:
              f_link = fam_nodes[child_of]['tag'] +':'+ fam_nodes[child_of]['key']
              i_link = indi_nodes[indi]['tag'] +':'+ indi_nodes[indi]['key']

              if reverse_links:
                 print( i_link + ' -> ' + f_link + ';' )
              else:
                 print( f_link + ' -> ' + i_link + ';' )


def find_person( person, item ):
    # it is possible that the selected person is not found
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
       found = readgedcom.find_individuals( data, item, person )
       if found:
          # just take the first one
          result = found[0]

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


def get_individuals( who_to_include, the_person ):
    global the_individuals
    global the_families

    result = True

    if who_to_include == 'all':
       for indi in data[ikey]:
           the_individuals.append( indi )
       for fam in data[fkey]:
           the_families.append( fam )

    else:
       # the existance of a personid value should already have been checked

       print( 'Selected person', the_person, '=', get_name(the_person, 'display'), file=sys.stderr )
       the_individuals.append( the_person )

       if who_to_include == 'ancestors':
          print( 'Output ancestors', file=sys.stderr )
          add_ancestors( the_person )

       elif who_to_include == 'descendents':
          print( 'Output descendents', file=sys.stderr )
          add_descendents( the_person )

       elif who_to_include == 'branch':
          print( 'Output ancestors and descendents', file=sys.stderr )
          add_ancestors( the_person )
          add_descendents( the_person )

       else:
          # unlikley to get here, but just in case i've made a typo
          print( 'Unknown option for include:', who_to_include, file=sys.stderr )
          result = False

    return result


def json_ancestors( indi ):
    results = dict()
    if indi in the_individuals:
       results[indi] = dict()
       results[indi]['name'] = get_name_json( indi )
       # they get a parent list, but it might be empty
       results[indi]['child_of'] = dict()
       if 'famc' in data[ikey][indi]:
          fam = data[ikey][indi]['famc'][0]

          results[indi]['child_of']['id'] = fam
          results[indi]['child_of']['parents'] = []
          # potentially add a marriage date here too

          for parent in ['wife','husb']:
              if parent in data[fkey][fam]:
                 parent_id = data[fkey][fam][parent][0]
                 results[indi]['child_of']['parents'].append( json_ancestors( parent_id ) )

    return results


def json_descendents( indi ):
    results = dict()
    if indi in the_individuals:
       results[indi] = dict()
       results[indi]['name'] = get_name_json( indi )
       # they get a family, but it might be empty
       results[indi]['families'] = []
       if 'fams' in data[ikey][indi]:
          for fam in data[ikey][indi]['fams']:
              other = find_other_partner( indi, fam )

              fam_info = dict()
              # potentially add a marriage date here too
              fam_info['id'] = fam
              fam_info['with_id'] = other
              fam_info['with_name'] = get_name_json( other )
              # they get a child list, but it might be empty
              fam_info['children'] = []

              if 'chil' in data[fkey][fam]:
                 for child in data[fkey][fam]['chil']:
                     fam_info['children'].append( json_descendents( child ) )

              results[indi]['families'].append( fam_info )
    return results


def output_json( the_person ):
    output = dict()

    # the contents are slightly different depending on the direction
    if options['include'] == 'ancestors':
       output = json_ancestors( the_person )

    else:
       output = json_descendents( the_person )

    json.dump( output, indent=1, fp=sys.stdout )


def output_data( out_format, reverse_links, thickness, picked_person ):
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

    elif out_format in ['dot','dot2']:
       style2 = out_format == 'dot2'

       dot_header()
       dot_setup( thickness )

       n_nodes = dot_families( style2, n_nodes, indi_nodes, fam_nodes )
       n_nodes = dot_not_families( n_nodes, indi_nodes )
       dot_connectors( indi_nodes, fam_nodes, reverse_links )

       dot_trailer()

    elif out_format == 'json':
       output_json( picked_person )

    else:
       # unlikely to get here, but just in case i've made a typo
       print( 'Unknown format', out_format, file=sys.stderr )
       result = False

    return result


def data_ok():
    result = False
    # it is possible to have a tree with no families,
    # but individuals are required
    if ikey in data:
       if len( data[ikey] ) > 0:
          result = True
       else:
          print( 'Data is empty', file=sys.stderr )
    else:
       print( 'Data not correct format.', file=sys.stderr )
    return result


def options_ok( program_options ):
    result = True

    if program_options['format'] == 'json':
       exclude = ['all','branch']
       if program_options['include'] in exclude:
          print( 'JSON format is not compatible with including one of', exclude, file=sys.stderr )
          result = False

    if program_options['include'] != 'all':
       if program_options['personid'] is None:
          print( 'include other than "all" requires a personid', file=sys.stderr )
          result = False

    return result


options = get_program_options()

readgedcom = load_my_module( 'readgedcom', options['libpath'] )

ikey = readgedcom.PARSED_INDI
fkey = readgedcom.PARSED_FAM

data = readgedcom.read_file( options['infile'] )

# find the people that should be output
the_individuals = []
the_families = []

exit_code = 1

if data_ok():
   if options_ok( options ):
      indi = None
      if options['include'] != 'all':
         indi = find_person( options['personid'], options['iditem'] )
         if indi is None:
            print( 'Did not locate specified person', options['personid'], 'in', options['iditem'], file=sys.stderr )
            sys.exit(exit_code)
      if get_individuals( options['include'], indi ):
         if output_data( options['format'], options['reverse'], options['thick'], indi ):
            exit_code = 0

sys.exit( exit_code )
