from dataclasses import dataclass


@dataclass
class Topology:
    """
    Class representing topologies for network-on-chips.
    """

    name: str
    num_nodes: int
    args: str

    def to_dict(self) -> dict:
        return {
            "topo_name": self.name,
            "topo_num_nodes": self.num_nodes,
            "topo_args": self.args,
        }
