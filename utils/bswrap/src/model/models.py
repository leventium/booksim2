from dataclasses import dataclass


@dataclass
class Topology:
    name: str
    num_nodes: int
    links: str

    def to_dict(self) -> dict:
        return {
            "topo_name": self.name,
            "topo_num_nodes": self.num_nodes,
            "topo_links": self.links,
        }


@dataclass
class Config:
    topo: Topology

    routing_function: str
    traffic_type: str
    sim_count: int

    def to_dict(self) -> dict:
        d = {
            "cfg_routing_func": self.routing_function,
            "cfg_traffic_type": self.traffic_type,
            "cfg_sim_count": self.sim_count,
        }
        d.update(self.topo.to_dict())
        return d


@dataclass
class Result:
    config: Config

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

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d.pop("config")
        d.update(self.config.to_dict())
        return d
