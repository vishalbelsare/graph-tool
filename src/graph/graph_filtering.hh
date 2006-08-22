// graph-tool -- a general graph modification and manipulation thingy
//
// Copyright (C) 2006  Tiago de Paula Peixoto <tiago@forked.de>
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#ifndef FILTERING_HH
#define FILTERING_HH

#include <boost/graph/graph_traits.hpp>
#include <boost/graph/filtered_graph.hpp>
#include <boost/graph/reverse_graph.hpp>
#include <boost/mpl/vector.hpp>
#include <boost/mpl/map.hpp>
#include <boost/mpl/for_each.hpp>
#include <boost/mpl/at.hpp>
#include <boost/mpl/or.hpp>
#include <boost/mpl/if.hpp>
#include <boost/mpl/logical.hpp>
#include <boost/python/object.hpp>
#include <boost/python/dict.hpp>
#include <boost/python/extract.hpp>

#include "graph_adaptor.hh"
#include "graph_selectors.hh"
#include "graph_python_filtering.hh"

namespace graph_tool
{
using namespace boost;

//==============================================================================
// HardNumVertices()
//==============================================================================
struct HardNumVertices
{
    template <class Graph>
    size_t operator()(const Graph &g) const
    {
	size_t n = 0;
	typename graph_traits<Graph>::vertex_iterator v_iter, v_begin, v_end;
	tie(v_begin, v_end) = vertices(g);
	for (v_iter = v_begin; v_iter != v_end; ++v_iter)
	    n++;
	return n;
    }
};

//==============================================================================
// SoftNumVertices()
//==============================================================================
struct SoftNumVertices
{
    template <class Graph>
    size_t operator()(const Graph &g) const { return num_vertices(g); }
};

//==============================================================================
// HardNumEdges()
//==============================================================================
struct HardNumEdges
{
    template <class Graph>
    size_t operator()(const Graph &g) const
    {
	size_t n = 0;
	typename graph_traits<Graph>::edge_iterator e_iter, e_begin, e_end;
	tie(e_begin, e_end) = edges(g);
	for (e_iter = e_begin; e_iter != e_end; ++e_iter)
	    n++;
	return n;
    }
};

//==============================================================================
// SoftNumEdges()
//==============================================================================
struct SoftNumEdges
{
    template <class Graph> 
    size_t operator()(const Graph &g) const { return num_edges(g); }
};

//==============================================================================
// RangeFilter
//==============================================================================
template <class FilteredPropertyMap>
class RangeFilter
{
public:
    RangeFilter(){}
    typedef typename property_traits<FilteredPropertyMap>::value_type value_type;
    typedef typename property_traits<FilteredPropertyMap>::key_type key_type;
    RangeFilter(FilteredPropertyMap filtered_property, std::pair<value_type, value_type> range)
        : _filtered_property(filtered_property), _range(range) {}
    template <class VertexOrEdge>
    bool operator() (VertexOrEdge e) const 
    {
        // ignore if outside allowed range
        if ( _filtered_property[e] < _range.first || _filtered_property[e] > _range.second)
            return false;
        return true;
    }
private:
    FilteredPropertyMap _filtered_property;
    std::pair<value_type, value_type> _range;
};

typedef mpl::vector<mpl::bool_<true>, mpl::bool_<false> > reverse_check;
typedef mpl::vector<mpl::bool_<false> > never_reversed;
typedef mpl::vector<mpl::bool_<true> > always_reversed;
typedef mpl::vector<mpl::bool_<true>, mpl::bool_<false> > directed_check;
typedef mpl::vector<mpl::bool_<true> > always_directed;
typedef mpl::vector<mpl::bool_<false> > always_undirected;

template <class Graph, class Action>
struct check_reverse
{
    check_reverse(const Graph &g, Action a, bool reverse, bool& found): _g(g), _a(a), _reverse(reverse), _found(found) {}

    template <class Reverse>
    void operator()(Reverse) const
    {
	if (_reverse)
	{
	    reverse_graph<Graph> rg(_g);
	    _a(rg);
	    _found = true;
	}
    }

    void operator()(mpl::bool_<false>) const
    { 
	if (!_reverse)
	{
	    _a(_g);
	    _found = true;
	}
    }

    const Graph &_g;
    Action _a;
    bool _reverse;
    bool& _found;
};

template <class Graph, class Action, class ReverseCheck>
struct check_directed
{
    check_directed(const Graph &g, Action a, bool reverse, bool directed, bool& found)
	: _g(g), _a(a), _reverse(reverse), _directed(directed), _found(found) {}

    template <class Directed>
    void operator()(Directed)
    {
	if (_directed)
	    mpl::for_each<ReverseCheck>(check_reverse<Graph, Action>(_g, _a, _reverse, _found));
    }

    void operator()(mpl::bool_<false>)
    { 
	if (!_directed)
	{
	    UndirectedAdaptor<Graph> ug(_g);
	    _a(ug);
	    _found = true;
	}
    }

    const Graph &_g;
    Action _a;
    bool _reverse;
    bool _directed;
    bool& _found;
};

template <class Graph, class Action, class ReverseCheck, class DirectedCheck> 
void check_python_filter(const Graph& g, const GraphInterface &gi, Action a, bool& found, ReverseCheck, DirectedCheck)
{
    typedef PythonFilter<Graph,typename graph_traits<Graph>::vertex_descriptor> vertex_filter_t;
    typedef PythonFilter<Graph,typename graph_traits<Graph>::edge_descriptor> edge_filter_t;

    if (gi._edge_python_filter != python::object())
    {
	typedef filtered_graph<Graph, edge_filter_t, keep_all> efg_t;
	efg_t efg(g,edge_filter_t(g, gi._properties, gi._edge_python_filter), keep_all());

	if (gi._vertex_python_filter != python::object())
	{
	    typedef PythonFilter<efg_t, typename graph_traits<efg_t>::vertex_descriptor, mpl::bool_<true> > vertex_filter_t;
	    typedef filtered_graph<efg_t,keep_all,vertex_filter_t> vefg_t;
	    vefg_t vefg(efg,keep_all(),vertex_filter_t(efg, gi._properties, gi._vertex_python_filter));
	    mpl::for_each<DirectedCheck>(check_directed<vefg_t,Action,ReverseCheck>(vefg, a, gi._reversed, gi._directed, found));
	}
	else
	{
	    mpl::for_each<DirectedCheck>(check_directed<efg_t,Action,ReverseCheck>(efg, a, gi._reversed, gi._directed, found));
	}
    }
    else if (gi._vertex_python_filter != python::object())
    {
	typedef filtered_graph<Graph,keep_all,vertex_filter_t> vfg_t;
	vfg_t vfg(g,keep_all(),vertex_filter_t(g, gi._properties, gi._vertex_python_filter));
	mpl::for_each<DirectedCheck>(check_directed<vfg_t,Action,ReverseCheck>(vfg, a, gi._reversed, gi._directed, found));
    } 
    else
    {
	mpl::for_each<DirectedCheck>(check_directed<Graph,Action,ReverseCheck>(g, a, gi._reversed, gi._directed, found));
    }
}

template <class Action, class ReverseCheck, class DirectedCheck> 
void check_filter(const GraphInterface &g, Action a, ReverseCheck, DirectedCheck)
{
    typedef RangeFilter<GraphInterface::vertex_filter_map_t> vertex_filter_t;
    typedef RangeFilter<GraphInterface::edge_filter_map_t> edge_filter_t;
    
    bool found = false;

    if (g._edge_python_filter == python::object() && g._vertex_python_filter == python::object())
    {
	if (g._vertex_filter_property != "" && g._edge_filter_property != "")
	{	
	    typedef filtered_graph<GraphInterface::multigraph_t, edge_filter_t, vertex_filter_t> fg_t;
	    fg_t fg(g._mg, edge_filter_t(g._edge_filter_map, g._edge_range), vertex_filter_t(g._vertex_filter_map, g._vertex_range));
	    mpl::for_each<DirectedCheck>(check_directed<fg_t,Action,ReverseCheck>(fg, a, g._reversed, g._directed, found));
	}
	else if (g._vertex_filter_property != "")
	{
	    typedef filtered_graph<GraphInterface::multigraph_t, keep_all, vertex_filter_t> fg_t;
	    fg_t fg(g._mg, keep_all(), vertex_filter_t(g._vertex_filter_map, g._vertex_range));
	    mpl::for_each<DirectedCheck>(check_directed<fg_t,Action,ReverseCheck>(fg, a, g._reversed, g._directed, found));
	} 
	else if (g._edge_filter_property != "")
	{
	    typedef filtered_graph<GraphInterface::multigraph_t, edge_filter_t, keep_all> fg_t;
	    fg_t fg(g._mg, edge_filter_t(g._edge_filter_map, g._edge_range), keep_all());
	    mpl::for_each<DirectedCheck>(check_directed<fg_t,Action,ReverseCheck>(fg, a, g._reversed, g._directed, found));
	}
	else
	{
	    mpl::for_each<DirectedCheck>(check_directed<GraphInterface::multigraph_t,Action,ReverseCheck>(g._mg, a, g._reversed, g._directed, found));
	}
    }
    else
    {
	check_python_filter(g._mg, g, a, found, ReverseCheck(), DirectedCheck());
    }

    if (!found)
	throw GraphException("graph filtering error: filter not found");
    
}

} //graph_tool namespace 

#endif