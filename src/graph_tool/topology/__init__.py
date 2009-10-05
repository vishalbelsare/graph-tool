#! /usr/bin/env python
# graph_tool.py -- a general graph manipulation python module
#
# Copyright (C) 2007 Tiago de Paula Peixoto <tiago@forked.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
``graph_tool.topology`` - Topology related functions
----------------------------------------------------

Summary
+++++++

.. autosummary::
   :nosignatures:

   isomorphism
   min_spanning_tree
   dominator_tree
   topological_sort
   transitive_closure
   label_components
   label_biconnected_components

Contents
++++++++
"""

from .. dl_import import dl_import
dl_import("import libgraph_tool_topology")

from .. core import _prop, Vector_int32_t, _check_prop_writable, \
     _check_prop_scalar, Graph
import random, sys, numpy
__all__ = ["isomorphism", "min_spanning_tree", "dominator_tree",
           "topological_sort", "transitive_closure", "label_components",
           "label_biconnected_components"]

def isomorphism(g1, g2, isomap=False):
    """Check whether two graphs are isomorphisms. If `isomap` is True, a vertex
    :class:`~graph_tool.PropertyMap` with the isomorphism mapping is returned as
    well.
    """
    imap = g1.new_vertex_property("int32_t")
    iso = libgraph_tool_topology.\
           check_isomorphism(g1._Graph__graph,g2._Graph__graph,
                             _prop("v", g1, imap))
    if isomap:
        return iso, imap
    else:
        return iso


def min_spanning_tree(g, weights=None, root=None, tree_map=None):
    """
    Return the minimum spanning tree of a given graph.

    Parameters
    ----------
    g : :class:`~graph_tool.Graph`
        Graph to be used.
    weights : :class:`~graph_tool.PropertyMap` (optional, default: None)
        The edge weights. If provided, the minimum spanning tree will minimize
        the edge weights.
    root : :class:`~graph_tool.Vertex` (optional, default: None)
        Root of the minimum spanning tree. It this is provided, Prim's algorithm
        is used. Otherwise, Kruskal's algorithm is used.
    tree_map : :class:`~graph_tool.PropertyMap` (optional, default: None)
        If provided, the edge tree map will be written in this property map.

    Returns
    -------
    tree_map : :class:`~graph_tool.PropertyMap`
        Edge property map with mark the tree edges: 1 for tree edge, 0
        otherwise.

    Notes
    -----
    The algorithm runs with :math:`O(E\log E)` complexity, or :math:`O(E\log V)`
    if `root` is specified.

    Examples
    --------
    >>> from numpy.random import seed
    >>> seed(42)
    >>> g = gt.random_graph(100, lambda: (5, 5))
    >>> tree = gt.min_spanning_tree(g)
    >>> print tree.a
    [0 0 0 0 1 0 0 0 0 0 0 0 0 1 1 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 1 1 0 0 1 0 0
     0 1 1 0 0 0 1 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 0 0 0 0
     0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0
     0 0 0 1 0 0 0 0 1 0 0 0 0 0 1 0 0 0 1 0 0 0 0 1 0 0 0 1 1 0 0 0 0 1 0 0 0
     0 1 0 0 0 0 0 0 0 0 1 1 0 0 0 0 1 0 0 1 1 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1
     0 0 0 1 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 1 1 0 0 0 0 1 0 0
     0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0
     1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0
     0 0 1 1 0 0 0 0 1 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 1 0 0 0
     0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 1 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1
     0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 1 1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0
     0 0 1 0 1 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 1 0 0 1 1 0 0 0 0 1 0 0 0 1
     1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0
     0 0 0 1 0 0 0 1 1 0 0 0 0 1 0 0 0 1 1]

    References
    ----------
    .. [kruskal-shortest-1956] J. B. Kruskal.  "On the shortest spanning subtree
       of a graph and the traveling salesman problem",  In Proceedings of the
       American Mathematical Sofiety, volume 7, pages 48-50, 1956.
    .. [prim-shortest-1957] R. Prim.  "Shortest connection networks and some
       generalizations",  Bell System Technical Journal, 36:1389-1401, 1957.
    .. [boost-mst] http://www.boost.org/libs/graph/doc/graph_theory_review.html#sec:minimum-spanning-tree
    .. [mst-wiki] http://en.wikipedia.org/wiki/Minimum_spanning_tree
    """
    if tree_map == None:
        tree_map = g.new_edge_property("bool")
    if tree_map.value_type() != "bool":
        raise ValueError("edge property 'tree_map' must be of value type bool.")

    g.stash_filter(directed=True)
    g.set_directed(False)
    if root == None:
        libgraph_tool_topology.\
               get_kruskal_spanning_tree(g._Graph__graph,
                                         _prop("e", g, weights),
                                         _prop("e", g, tree_map))
    else:
        libgraph_tool_topology.\
               get_prim_spanning_tree(g._Graph__graph, int(root),
                                      _prop("e", g, weights),
                                      _prop("e", g, tree_map))
    g.pop_filter(directed=True)
    return tree_map

def dominator_tree(g, root, dom_map=None):
    """Return a vertex property map the dominator vertices for each vertex.

    Parameters
    ----------
    g : :class:`~graph_tool.Graph`
        Graph to be used.
    root : :class:`~graph_tool.Vertex`
        The root vertex.
    dom_map : :class:`~graph_tool.PropertyMap` (optional, default: None)
        If provided, the dominator map will be written in this property map.

    Returns
    -------
    dom_map : :class:`~graph_tool.PropertyMap`
        The dominator map. It contains for each vertex, the index of its
        dominator vertex.

    Notes
    -----
    A vertex u dominates a vertex v, if every path of directed graph from the
    entry to v must go through u.

    The algorithm runs with :math:`O((V+E)\log (V+E))` complexity.

    Examples
    --------
    >>> from numpy.random import seed
    >>> seed(42)
    >>> g = gt.random_graph(100, lambda: (2, 2))
    >>> tree = gt.min_spanning_tree(g)
    >>> g.set_edge_filter(tree)
    >>> root = [v for v in g.vertices() if v.in_degree() == 0]
    >>> dom = gt.dominator_tree(g, root[0])
    >>> print dom.a
    [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
      0 74  0  0  0 65  0  0  0 99  0  0  0  0  0  0  0  0 52  0  0  0  0  0 43
      0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 43  0  0  0  0  0  0  0  0  5
      0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 37]

    References
    ----------
    .. [dominator-bgl] http://www.boost.org/libs/graph/doc/lengauer_tarjan_dominator.htm

    """
    if dom_map == None:
        dom_map = g.new_vertex_property("int32_t")
    if dom_map.value_type() != "int32_t":
        raise ValueError("vertex property 'dom_map' must be of value type" +
                         " int32_t.")
    if not g.is_directed():
        raise ValueError("dominator tree requires a directed graph.")
    libgraph_tool_topology.\
               dominator_tree(g._Graph__graph, int(root),
                              _prop("v", g, dom_map))
    return dom_map

def topological_sort(g):
    """
    Return the topological sort of the given graph. It is returned as an array
    of vertex indexes, in the sort order.

    Notes
    -----
    The topological sort algorithm creates a linear ordering of the vertices
    such that if edge (u,v) appears in the graph, then v comes before u in the
    ordering. The graph must be a directed acyclic graph (DAG).

    The time complexity is :math:`O(V + E)`.

    Examples
    --------
    >>> from numpy.random import seed
    >>> seed(42)
    >>> g = gt.random_graph(30, lambda: (3, 3))
    >>> tree = gt.min_spanning_tree(g)
    >>> g.set_edge_filter(tree)
    >>> sort = gt.topological_sort(g)
    >>> print sort
    [21 12 28  1 13 23 25  0 19 22  2  3  4  6  9  5  7 26  8 29 16 10 11 17 14
     15 18 20 24 27]

    References
    ----------
    .. [topological-boost] http://www.boost.org/libs/graph/doc/topological_sort.html
    .. [topological-wiki] http://en.wikipedia.org/wiki/Topological_sorting

    """

    topological_order = Vector_int32_t()
    libgraph_tool_topology.\
               topological_sort(g._Graph__graph, topological_order)
    return numpy.array(topological_order)

def transitive_closure(g):
    """Return the transitive closure graph of g.

    Notes
    -----
    The transitive closure of a graph G = (V,E) is a graph G* = (V,E*) such that
    E* contains an edge (u,v) if and only if G contains a path (of at least one
    edge) from u to v. The transitive_closure() function transforms the input
    graph g into the transitive closure graph tc.

    The time complexity (worst-case) is :math:`O(VE)`.

    Examples
    --------
    >>> from numpy.random import seed
    >>> seed(42)
    >>> g = gt.random_graph(30, lambda: (3, 3))
    >>> tc = gt.transitive_closure(g)

    References
    ----------
    .. [transitive-boost] http://www.boost.org/libs/graph/doc/transitive_closure.html
    .. [transitive-wiki] http://en.wikipedia.org/wiki/Transitive_closure

    """

    if not g.is_directed():
        raise ValueError("graph must be directed for transitive closure.")
    tg = Graph()
    libgraph_tool_topology.transitive_closure(g._Graph__graph,
                                              tg._Graph__graph)
    return tg

def label_components(g, vprop=None, directed=None):
    """
    Label the components to which each vertex in the graph belongs. If the
    graph is directed, it finds the strongly connected components.

    Parameters
    ----------
    g : :class:`~graph_tool.Graph`
        Graph to be used.

    vprop : :class:`~graph_tool.PropertyMap` (optional, default: None)
        Vertex property to store the component labels. If none is supplied, one
        is created.

    directed : bool (optional, default:None)
        Treat graph as directed or not, independently of its actual
        directionality.

    Returns
    -------
    comp : :class:`~graph_tool.PropertyMap`
        Vertex property map with component labels.

    Notes
    -----
    The components are arbitrarily labeled from 0 to N-1, where N is the total
    number of components.

    The algorithm runs in :math:`O(V + E)` time.

    Examples
    --------
    >>> from numpy.random import seed
    >>> seed(43)
    >>> g = gt.random_graph(100, lambda: (1, 1))
    >>> comp = gt.label_components(g)
    >>> print comp.get_array()
    [0 1 1 1 0 2 1 1 3 0 1 2 1 2 4 2 2 1 2 1 0 3 1 1 2 0 2 2 1 4 0 0 0 4 0 1 2
     1 0 4 2 2 0 2 1 0 0 1 2 0 1 2 2 2 1 2 0 1 1 2 1 2 2 1 2 1 1 2 0 0 1 2 1 0
     1 1 1 2 2 2 2 1 0 1 0 2 0 4 2 2 2 2 0 0 0 0 1 2 2 3]
    """

    if vprop == None:
        vprop = g.new_vertex_property("int32_t")

    _check_prop_writable(vprop, name="vprop")
    _check_prop_scalar(vprop, name="vprop")

    if directed != None:
        g.stash_filter(directed=True)
        g.set_directed(directed)

    libgraph_tool_topology.\
          label_components(g._Graph__graph, _prop("v", g, vprop))

    if directed != None:
        g.pop_filter(directed=True)
    return vprop

def label_biconnected_components(g, eprop=None, vprop=None):
    """
    Label the edges of biconnected components, and the vertices which are
    articulation points.

    Parameters
    ----------
    g : :class:`~graph_tool.Graph`
        Graph to be used.

    eprop : :class:`~graph_tool.PropertyMap` (optional, default: None)
        Edge property to label the biconnected components.

    vprop : :class:`~graph_tool.PropertyMap` (optional, default: None)
        Vertex property to mark the articulation points. If none is supplied,
        one is created.


    Returns
    -------
    bicomp : :class:`~graph_tool.PropertyMap`
        Edge property map with the biconnected component labels.
    articulation : :class:`~graph_tool.PropertyMap`
        Boolean vertex property map which has value 1 for each vertex which is
        an articulation point, and zero otherwise.
    nc : int
        Number of biconnected components.

    Notes
    -----

    A connected graph is biconnected if the removal of any single vertex (and
    all edges incident on that vertex) can not disconnect the graph. More
    generally, the biconnected components of a graph are the maximal subsets of
    vertices such that the removal of a vertex from a particular component will
    not disconnect the component. Unlike connected components, vertices may
    belong to multiple biconnected components: those vertices that belong to
    more than one biconnected component are called "articulation points" or,
    equivalently, "cut vertices". Articulation points are vertices whose removal
    would increase the number of connected components in the graph. Thus, a
    graph without articulation points is biconnected. Vertices can be present in
    multiple biconnected components, but each edge can only be contained in a
    single biconnected component.

    The algorithm runs in :math:`O(V + E)` time.

    Examples
    --------
    >>> from numpy.random import seed
    >>> seed(42)
    >>> g = gt.random_graph(100, lambda: 2, directed=False)
    >>> comp, art, nc = gt.label_biconnected_components(g)
    >>> print comp.a
    [0 0 1 0 0 0 1 2 0 0 1 3 0 0 1 1 0 0 0 0 0 1 0 0 0 0 0 1 0 1 1 0 0 0 2 2 3
     1 0 0 0 1 0 0 1 1 0 1 1 0 0 0 0 0 0 1 3 1 1 1 1 0 0 0 0 0 0 0 1 0 0 1 1 0
     0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 1 1 1 0 0]
    >>> print art.a
    [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
     0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
     0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
    >>> print nc
    4

    """

    if vprop == None:
        vprop = g.new_vertex_property("bool")
    if eprop == None:
        eprop = g.new_edge_property("int32_t")

    _check_prop_writable(vprop, name="vprop")
    _check_prop_scalar(vprop, name="vprop")
    _check_prop_writable(eprop, name="eprop")
    _check_prop_scalar(eprop, name="eprop")

    g.stash_filter(directed=True)
    try:
        g.set_directed(False)
        nc = libgraph_tool_topology.\
             label_biconnected_components(g._Graph__graph, _prop("e", g, eprop),
                                          _prop("v", g, vprop))
    finally:
        g.pop_filter(directed=True)
    return eprop, vprop, nc