from dataclasses import dataclass

from topology import ITopology


@dataclass
class SimulationTask:
    topo: list[ITopology]
    routing_funcs: list[str]
    traffic_types: list[str]
    sim_counts: list[int]


@dataclass
class SimulationTaskLegacy:
    topo_names: list[str]
    num_nodes: list[int]
    links: list[str]

    routing_funcs: list[str]
    traffic_types: list[str]
    sim_counts: list[int]
