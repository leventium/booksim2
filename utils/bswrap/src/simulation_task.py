from dataclasses import dataclass


@dataclass
class SimulationTask:
    topo_names: list[str]
    num_nodes: list[int]
    links: list[str]

    routing_funcs: list[str]
    traffic_types: list[str]
    sim_counts: list[int]
