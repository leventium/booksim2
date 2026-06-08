import json
from itertools import product

from simulation_task import SimulationTask, SimulationTaskLegacy
from topology import ITopology, TopoNode


class Circulant(ITopology):
    def __init__(self, num_nodes: int, links: list[int]) -> None:
        self._num_nodes = num_nodes
        self._links = links

    def get_topology_graph(self) -> list[TopoNode]:
        res: list[TopoNode] = [TopoNode(i, []) for i in range(self._num_nodes)]

        for i in range(self._num_nodes):
            for link in self._links:
                node_idx = (i + link) % self._num_nodes
                res[i].links.append(res[node_idx])
                res[node_idx].links.append(res[i])

        return res

    def get_topology_num_nodes(self) -> int:
        return self._num_nodes

    def get_topology_name(self) -> str:
        return "circulant"

    def get_topology_descriptor(self) -> str:
        res = f"circulant_c{self._num_nodes}"
        for link in self._links:
            res += f"_{link}"
        return res

    def get_topology_arguments(self) -> str:
        return json.dumps(
            {
                "num_nodes": self._num_nodes,
                "links": self._links,
            }
        )


TASK_CONFIG = [
    SimulationTask(  # New style
        topo=[
            Circulant(num_nodes, links)
            for num_nodes, links in product([10, 20, 30], ([1, 2], [1, 4]))
        ],
        routing_funcs=["min"],
        traffic_types=["uniform"],
        sim_counts=[3],
    ),
    SimulationTaskLegacy(  # Old style
        topo_names=["circulant"],
        num_nodes=[10, 20, 30],
        links=["1,2", "1,4"],
        routing_funcs=["min"],
        traffic_types=["uniform"],
        sim_counts=[3],
    ),
]
