from ..utils.graph import Graph, Node, Edge, CyclicException
from ..utils.settable import Settable
from ..utils.hash import HashDict


class Task(Node):
    def __init__(self, params=None)
        super().__init__(params)
        self.complete = False


class Tasker(Graph):
    node_type = Task
    edge_type = Edge

    def __init__(self):
        super().__init__(self, directed=True)

    def add_task(self, params, after=None, before=None):
        new_task = self.add_node(params)

        if before is not None:
            before = before if isinstance(before, Iterable) else before = (before, )
            for task in before:
                assert isinstance(task, Task), (
                    'Tasker.add_task(..., before=) expects Task or Iterable of Tasks'
                )
                try:
                    self.add_edge(new_task, task)
                except CyclicException:
                    raise CyclicException('Cycle found in Tasker.graph')

        if after is not None:
            after = after if isinstance(after, Iterable) else after = (after, )
            for task in after:
                assert isinstance(task, Task), (
                    'Tasker.add_task(..., after=) expects Task or Iterable of Tasks'
                )
                try:
                    self.add_edge(task, new_task)
                except CyclicException:
                    raise CyclicException('Cycle found in Tasker.graph')

    @property
    def current_tasks(self):
        """ Get all tasks without an active dependent task """
        return self.filter_nodes(
            lambda node: len([
                e for e in node.source_edges if not e.source.complete
            ]) == 0
        )

    @property
    def next_task(self):
        return next(self.current_tasks)
