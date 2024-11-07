from .hash import create_hash, HashDict
from .repr import NiceRepr
from .settable import Settable


class Node(Settable, NiceRepr):
    def __init__(self, params=None, id=None, graph=None):
        super().__init__(params)
        self._repr_ = ['id', self.params]
        self.graph = graph
        self.source_edges = []
        self.target_edges = []
        self.id = id
        if self.graph:
            self.graph._register_node(self)
        if self.id is None:
            self.id = create_hash(8)

    def __eq__(self, other):
        return self.id == other or self is other

    @property
    def edges(self):
        return self.source_edges + self.target_edges

    def _register_edge(self, edge, am_source=True):
        if am_source:
            self.target_edges.append(edge)
        else:
            self.source_edges.append(edge)

    @property
    def source_nodes(self):
        return [edge.source for edge in self.source_edges]

    @property
    def target_nodes(self):
        return [edge.target for edge in self.target_edges]

    def add_edge(self, target_node, params=None):
        return Edge(self, target_node, params=params, graph=self.graph)


class Edge(Settable, NiceRepr):
    def __init__(self, node_a, node_b, params={}, id=None, graph=None):
        super().__init__(params)
        self._repr_ = ['id', self.params]
        self.graph = graph
        self.nodes = (node_a, node_b)
        self['source'] = node_a
        self['target'] = node_b
        self.id = id
        if self.graph:
            self.graph._register_edge(self)
        if self.id is None:
            self.id = id or create_hash(8)
        node_a._register_edge(self, am_source=True)
        node_b._register_edge(self, am_source=False)



class Graph(NiceRepr):
    _repr_ = ['node_list', 'edge_list']
    node_type = Node
    edge_type = Edge

    def __init__(self, directed=False):
        self.nodes = HashDict()
        self.edges = HashDict()
        self.directed = directed
        self.hash_size = 3

    @property
    def node_list(self):
        return [_ for _ in self.nodes.values()]

    @property
    def edge_list(self):
        return [_ for _ in self.edges.values()]

    def add_node(self, params={}, id=None):
        return self.node_type(params, id, graph=self)

    def get_node(self, node_id):
        return node_id if isinstance(node_id, Node) else self.nodes[node_id]

    def add_edge(self, source, target, params={}):
        source = self.get_node(source)
        target = self.get_node(target)
        return self.edge_type(source, target, params=params, graph=self)

    def filter_nodes(self, condition):
        return (node for node in self.nodes.values() if condition(node))

    def filter_edges(self, condition):
        return (edge for edge in self.edges.values() if condition(edge))

    def check_for_path(self, source, target):
        visited = {}
        source = self.get_node(source)
        target = self.get_node(target)


        def recur(node):
            if node == target:
                return True

            visited[node.id] = True

            # Recur for all the vertices adjacent to this vertex
            for neighbor in node.target_nodes:
                if not visited.get(neighbor.id, False):
                    if recur(neighbor):
                        return True

            return False

        return recur(source)

    def _check_graph_for_cycle(self):
        visited = {node.id: False for node in self.nodes.values()}
        rec_stack = {node.id: False for node in self.nodes.values()}

        def _recur(node):
            # Mark the current node as visited and adds to recursion stack
            visited[node.id] = True
            rec_stack[node.id] = True

            # Recur for all neighbours
            for neighbour in node.target_nodes:
                if not visited[neighbour.id]:
                    if _recur(neighbour):
                        return True
                elif rec_stack[neighbour.id]:
                    return True

            # The node needs to be popped from recursion stack before function ends
            rec_stack[node.id] = False
            return False

        for node in self.nodes.values():
            if not visited[node.id]:   # Don't revisit already visited nodes
                if _recur(node):
                    return True

        return False

    def _register_node(self, node):
        if self.directed and len(node.edges) > 0:
            raise NotImplementedError(
                'Cycle detection when adding a Node with Edges not implemented.'
            )
        if node.id is None:
            node.id = self.nodes.put(node)
        else:
            assert node.id not in self.nodes, (
                f"A node with id {node.id} already exists in the graph"
            )
            self.nodes[id] = node

    def _register_edge(self, edge):
        if self.directed:
            if self.check_for_path(edge.target, edge.source):
                raise CyclicException()
        if edge.id is None:
            edge.id = self.edges.put(edge)
        else:
            assert id not in self.edges, (
                f"An edge with id {edge.id} already exists in the graph"
            )
            self.edges[id] = edge


class CyclicException(Exception):
    """Exception raised when a cycle is detected in the graph."""

    def __init__(self, message="Cycle detected"):
        self.message = message
        super().__init__(self.message)
