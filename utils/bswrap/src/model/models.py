from dataclasses import dataclass

from topology import ITopology, Topology


@dataclass
class Config:
    """
    Class representing simulation configuration.
    """

    routing_function: str
    traffic_type: str
    sim_count: int

    topo: ITopology | Topology | None = None

    def get_description(self) -> str:
        if self.topo is None:
            raise ValueError("Topology must be specified.")
        topo_name = (
            self.topo.get_topology_name()
            if isinstance(self.topo, ITopology)
            else self.topo.name
        )
        topo_num_nodes = (
            self.topo.get_topology_num_nodes()
            if isinstance(self.topo, ITopology)
            else self.topo.num_nodes
        )
        return f"{topo_name}_N{topo_num_nodes}_R{self.routing_function}"

    def to_dict(self) -> dict:
        if self.topo is None:
            raise ValueError("No topology specified.")

        d = {
            "cfg_routing_func": self.routing_function,
            "cfg_traffic_type": self.traffic_type,
            "cfg_sim_count": self.sim_count,
        }
        d.update(self.topo.to_dict())
        return d


@dataclass
class Result:
    """
    Class representing simulation result.
    """

    packet_latency_min: float
    packet_latency_max: float
    packet_latency_avg: float
    network_latency_min: float
    network_latency_max: float
    network_latency_avg: float
    flit_latency_min: float
    flit_latency_max: float
    flit_latency_avg: float
    fragmentation_min: float
    fragmentation_max: float
    fragmentation_avg: float
    injected_packet_rate_min: float
    injected_packet_rate_max: float
    injected_packet_rate_avg: float
    accepted_packet_rate_min: float
    accepted_packet_rate_max: float
    accepted_packet_rate_avg: float
    injected_flit_rate_min: float
    injected_flit_rate_max: float
    injected_flit_rate_avg: float
    accepted_flit_rate_min: float
    accepted_flit_rate_max: float
    accepted_flit_rate_avg: float
    injected_packet_size_avg: float
    accepted_packet_size_avg: float
    hops_avg: float

    config: Config | None = None

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d.pop("config")
        d.update(self.config.to_dict())
        return d
