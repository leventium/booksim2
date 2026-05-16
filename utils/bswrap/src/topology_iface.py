from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TopoNode:
    """
    Represents a topology's node and its links with other nodes.
    """

    # Must be a unique in node list integer
    node_id: int
    # Pointers to other nodes that current node have links with
    links: list["TopoNode"]


class ITopology(ABC):
    """
    Interface for topology.
    Inherited class must represent scalable topology type and implement
    presented methods while hiding its parameters in private members.
    """

    @abstractmethod
    def get_topology_graph(self) -> list[TopoNode]:
        """
        Return list of 'TopoNode' objects representing all the nodes
        and its links in topology.
        """
        pass

    @abstractmethod
    def get_topology_num_nodes(self) -> int:
        """
        Returns a number of nodes in topology.
        """
        pass

    @abstractmethod
    def get_topology_descriptor(self) -> str:
        """
        Returns a topology desciptor that will be shown in progress bar.
        It should display a key parameter values of topology object.
        """
        pass

    @abstractmethod
    def get_topology_arguments(self) -> str:
        """
        Returns a json serialized string of all topology's parameter values.
        It will be used in 'topo_args' field in CSV result.
        """
        pass
