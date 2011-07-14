# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Methods that make network node diagrams
# -----------------------------------------------------------------------------------------------------------------

from narracat_constants import *
from narracat_stats import *
from narracat_data import *

import colorsys

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

#import networkx as nx
#import pygraphviz as pgv

# I did NOT get this to work with networkx. too many spacing problems.
# ended up writing out *.dot files for Graphviz to read. That worked.
# will need more attention at some point.

# -----------------------------------------------------------------------------------------------------------------
# graphing methods that write one file
# -----------------------------------------------------------------------------------------------------------------
	
def graphNetworkNodeDiagram(networkFileName, graphName, pngFileName, pngFilePath, lineUp=False):
	
	pngFilePath += "network" + os.sep
	if not os.path.exists(pngFilePath):
		os.mkdir(pngFilePath)
	
	graph = nx.Graph()
	groups = []
	conditions = []
	types = []
	
	networkFile = open(networkFileName, "U")
	try:
		nodesAndEdges = csv.reader(networkFile)
		wrapLines = 3
		for row in nodesAndEdges:
			if len(row) > 1 and row[0].find(";") != 0:
				condition = row[0].strip()
				if condition and not condition in conditions: conditions.append(condition)
				group = row[1].strip()
				if group and not group in groups: groups.append(group)
				type = row[2].strip()
				if type and not type in types: types.append(type)
				level = row[3].strip()
				parent = row[4].strip()
				originalName = row[5].strip()
				newName = None
				if len(row) > 6:
					newName = row[6].strip()
				if newName:
					name = newName
				else:
					name = originalName
				if not lineUp:
					words = name.split(" ", wrapLines)
					name = "\n".join(words)
				graph.add_node(name, condition=condition, group=group, type=type, level=level)
				if len(parent) > 0:
					if not lineUp:
						parentWords = parent.split(" ", wrapLines)
						parent = "\n".join(parentWords)
					graph.add_edge(name, parent)
					
		# condition group and type were custom subsets, but I'm leaving it in, in case I need subsets again.
		for condition in conditions:			
			for group in groups:
				for type in types:
					# http://groups.google.com/group/networkx-discuss/browse_thread/thread/9abc080dd95c0373
					subgraph = graph.subgraph([n for n,attrdict in graph.node.items() 
							if (attrdict['condition'] == condition and attrdict['group'] == group and attrdict['type'] == type) ])
					numNodes = len(subgraph.nodes())
					if numNodes >= 10: 
						
						graphName = '%s %s %s network' % (condition, group, type)
						dotFile = open(pngFilePath + cleanTextForFileName(graphName) + ".dot", 'w')
						try:
							dotFile.write('graph "%s" {\n' % graphName)
							
							dotFile.write('graph [\n')
							#dotFile.write('  aspect="1.0, 20",\n')
							dotFile.write('  ratio = auto;\n')
							#dotFile.write('  size="6, 4",\n')
							dotFile.write('  rankdir="LR",\n')
							#dotFile.write('  overlap=scale,\n')
							#dotFile.write('  fontsize="16",\n')
							dotFile.write('  ];\n')
							
							dotFile.write('node [shape=hexagon, style=filled];\n')
							
							dotFile.write('{node [fillcolor=skyblue]\n')
							for node in subgraph.nodes(data=True):
								if node[1]['level'] == "Cluster":
									dotFile.write('  "%s";\n' % node[0].replace("\n", " "))
							dotFile.write('  }\n')
								
							"""
							dotFile.write('{rank=same;\n')
							for node in subgraph.nodes(data=True):
								if node[1]['level'] == "Cluster":
									dotFile.write('  "%s";\n' % node[0].replace("\n", " "))
							dotFile.write('  }\n')
							"""

							dotFile.write('{node [fillcolor=orange]\n')
							for node in subgraph.nodes(data=True):
								if node[1]['level'] == "Archetype":
									dotFile.write('  "%s";\n' % node[0].replace("\n", " "))
							dotFile.write('  }\n')

							"""
							dotFile.write('{rank=same;\n')
							for node in subgraph.nodes(data=True):
								if node[1]['level'] == "Archetype":
									dotFile.write('  "%s";\n' % node[0].replace("\n", " "))
							dotFile.write('  }\n')

							dotFile.write('{rank=same;\n')
							for node in subgraph.nodes(data=True):
								if node[1]['level'] == "Attribute":
									dotFile.write('  "%s";\n' % node[0].replace("\n", " "))
							dotFile.write('  }\n')
							"""

							dotFile.write('{node [fillcolor=lightgray]\n')
							for node in subgraph.nodes(data=True):
								if node[1]['level'] == "Attribute":
									dotFile.write('  "%s";\n' % node[0].replace("\n", " "))
							dotFile.write('  }\n')

							for edge in subgraph.edges(data=True):
								#print edge[0].replace("\n", " "), '->', edge[1].replace("\n", " ")
								dotFile.write('  "%s" -- "%s"\n' % (edge[0].replace("\n", " "), edge[1].replace("\n", " ")))
							dotFile.write("}\n")
						finally:
							dotFile.close()
						
						
						"""
						# YEAH, this didn't work so I gave up on it. but may try again later.
						
						plt.clf()
						
						# trying to size things right so labels don't overlap, kludgey, networkx not super for drawing
						figWidth = max(numNodes // 5, 2)
						figHeight = max(numNodes // 6, 2)
						scale = numNodes / 5.0
						fontSize = max(numNodes // 10, 4)
						nodeSize = numNodes * 10
						spacing = 10 
						
						#print 'nodes', numNodes, 'width', figWidth, 'height', figHeight, 'scale', scale, 'font size', fontSize, 'node size', nodeSize
						
						figure = plt.figure(figsize=(figWidth, figHeight))
						
						numClusterNodes = 0
						numArchetypeNodes = 0
						numAttributeNodes = 0
						for node in subgraph.nodes(data=True):
							level = node[1]['level']
							if level == "Cluster":
								numClusterNodes += 1
							elif level == "Archetype":
								numArchetypeNodes += 1
							elif level == "Attribute":
								numAttributeNodes += 1

						clusterNodes = []
						archetypeNodes = []
						attributeNodes = []
						
						positions = {}
						for node in subgraph.nodes(data=True):
							level = node[1]['level']
							if level == "Cluster":
								clusterNodes.append(node[0])
								positions[node[0]] = [0, 1.0 * len(clusterNodes) / numClusterNodes]
								#print positions[node[0]]
							elif level == "Archetype":
								archetypeNodes.append(node[0])
								positions[node[0]] = [2, 1.0 * len(archetypeNodes) / numArchetypeNodes]
								#print positions[node[0]]
							elif level == "Attribute":
								attributeNodes.append(node[0])
								positions[node[0]] = [1, 1.0 * len(attributeNodes) / numAttributeNodes]
								#print "%s\t%s\t%s\t%s\t%s\t%s" % (node[1]['condition'], node[1]['group'], node[1]['type'], node[1]['level'], node[0].replace("\n", " "), node[0].replace("\n", " "))
							
						if not lineUp:
							# trying to optimize positions!!
							positionsWithDistances = {}
							maxOverallMinDistance = 0
							for iteration in range(100):
								positions = nx.spring_layout(subgraph, iterations=15, scale=scale)
								minDistance = 10000
								for node in positions.keys():
									p1 = positions[node]
									for anotherNode in positions.keys():
										if anotherNode != node:
											p2 = positions[anotherNode]
											distance = (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1])
											if distance < minDistance:
												minDistance = distance
								positionsWithDistances[minDistance] = positions
								if minDistance > maxOverallMinDistance:
									maxOverallMinDistance = minDistance
							positions = positionsWithDistances[maxOverallMinDistance]
						
						nx.draw_networkx_nodes(subgraph, positions, nodelist=attributeNodes, node_shape='h', node_size=nodeSize, node_color='#BBFFFF', alpha=0.3)
						nx.draw_networkx_nodes(subgraph, positions, nodelist=clusterNodes, node_shape='h', node_size=nodeSize, node_color='yellow', alpha=0.3)
						nx.draw_networkx_nodes(subgraph, positions, nodelist=archetypeNodes, node_shape='h', node_size=nodeSize, node_color='red', alpha=0.3)
			
						nx.draw_networkx_edges(subgraph, positions,  with_labels=False, width=0.5, alpha=0.3)
						nx.draw_networkx_labels(subgraph, positions, font_size=fontSize)
						
						plt.axis('off')
						fileName = '%s %s %s network' % (condition, group, type)
						if lineUp:
							fileName = "LINED UP " + fileName
						plt.text(0.95, 0.01, fileName, horizontalalignment='right', transform=figure.transFigure, fontsize=fontSize*2)
						#plt.savefig(pngFilePath + cleanTextForFileName(fileName) + ".png", dpi=200)
						plt.close(figure)
						
						#nx.write_dot(subgraph, pngFilePath + cleanTextForFileName(fileName) + ".dot")
						
						print "file %s written." % fileName 
						"""
	finally:
		networkFile.close()

