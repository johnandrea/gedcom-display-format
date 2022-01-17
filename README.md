# gedcom-display-format
Convert a GEDCOM file to a format for display in network visualization.

The display may be of limited value for large trees as it takes a long time to arrange into a useful structure.

## Display ##

Output files can be used in display tools such as:
- Cytoscape: https://cytoscape.org

## Usage ##

```
gedcom-display-format.py gedcom-filename > formatted-file
```

## Formats ##

Currently only produces GraphML ( http://graphml.graphdrawing.org )

## Installation ##

- Requires python 3.6+
- Copy Python file and supporting style file(s).
- also requires gedcom library [readgedcom.py](https://github.com/johnandrea/readgedcom)
