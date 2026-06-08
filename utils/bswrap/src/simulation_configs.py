from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from circulant_builder import Circulant
from model import Config
from topology import ITopology

# class RoutingFunc(StrEnum):
#     min = "min"
#     dor = "dor"
#     dim_order = "dim_order"


# class TrafficType(StrEnum):
#     uniform = "uniform"
#     bitcomp = "bitcomp"
#     bitrev = "bitrev"
#     shuffle = "shuffle"
#     transpose = "transpose"
#     tornado = "tornado"
#     neighbor = "neighbor"
#     randperm = "randperm"


@dataclass
class TopoIndependentConfig:
    routing_func: str
    traffic: str
    sim_count: int


class ISimConfig(ABC):
    config_template = """\
routing_function = {routing_func};
traffic          = {traffic_type};
sample_period    = 10000;
injection_rate   = 0.0001;
sim_count        = {sim_count};
num_vcs          = 4;
vc_buf_size      = 4;

"""

    def _fill_base_config(self, conf: TopoIndependentConfig) -> str:
        return self.config_template.format(
            routing_func=conf.routing_func,
            traffic_type=conf.traffic,
            sim_count=conf.sim_count,
        )

    def get_indep_namepart(self, conf: TopoIndependentConfig):
        return f"_F{conf.routing_func}_T{conf.traffic}_S{conf.sim_count}"

    @abstractmethod
    def create_config(self, configs_dir: Path) -> Path:
        """
        Creates config in filesystem and returns its path.
        """
        pass

    @abstractmethod
    def get_topology_name(self) -> str:
        """
        Creates configuration string descriptor.
        Must display all the parameters of its configuration.
        """
        pass


class AnyConfig(ISimConfig):
    topo_config = """\
topology = anynet;
network_file = {anynet_filename};

"""

    def __init__(self, config: Config) -> None:
        if not isinstance(config.topo, ITopology):
            raise ValueError("Topology in config must implement ITopology.")
        self._config = config
        self._topo = config.topo
        self._indep_conf = TopoIndependentConfig(
            routing_func=self._config.routing_function,
            traffic=self._config.traffic_type,
            sim_count=self._config.sim_count,
        )

    def create_config(self, configs_dir: Path) -> Path:
        topology_path = configs_dir.joinpath("topo_" + self.get_topology_name())
        config_path = configs_dir.joinpath("config_" + self.get_topology_name())

        with open(topology_path, "w") as file:
            topo_graph = self._topo.get_topology_graph()
            for node in topo_graph:
                file.write(f"router {node.node_id} node {node.node_id}")
                for node_link in node.links:
                    file.write(f" router {node_link.node_id}")
                file.write("\n")

        with open(config_path, "w") as file:
            config_content = self.topo_config.format(
                anynet_filename=topology_path,
            ) + self._fill_base_config(self._indep_conf)
            file.write(config_content)

        return config_path

    def get_topology_name(self) -> str:
        return self._topo.get_topology_descriptor() + self.get_indep_namepart(
            self._indep_conf
        )


class CirculantConfig(ISimConfig):
    topo_config = """\
topology = anynet;
network_file = {anynet_filename};

"""

    def __init__(self, num_nodes: int, links: list[int], config: TopoIndependentConfig):
        self.circulant = Circulant(num_nodes, links)
        self.num_nodes = num_nodes
        self.links = links
        self.config = config

    @staticmethod
    def new_config(
        num_nodes: int, links: str, routing_func: str, traffic_type: str, sim_count: int
    ) -> ISimConfig:
        return CirculantConfig(
            num_nodes,
            list(map(int, links.split(","))),
            TopoIndependentConfig(
                routing_func,
                traffic_type,
                sim_count,
            ),
        )

    def get_topology_name(self) -> str:
        res = f"circulant_c{self.num_nodes}"
        for link in self.links:
            res += f"_{link}"
        return res + self.get_indep_namepart(self.config)

    def create_config(self, configs_dir: Path) -> Path:
        config_path = configs_dir.joinpath("config_" + self.get_topology_name())
        topology_path = configs_dir.joinpath("topo_" + self.get_topology_name())

        config_content = self.topo_config.format(
            anynet_filename=topology_path,
        ) + self._fill_base_config(self.config)
        with open(topology_path, "w") as file:
            file.write(self.circulant.serialize_booksim())
        with open(config_path, "w") as file:
            file.write(config_content)

        return config_path


class CellTopoConfig(ISimConfig):
    def __init__(self, k: int, n: int, conf: TopoIndependentConfig):
        """
        K - Number of routers per dimension
        N - Network dimensions
        """
        self.k = k
        self.n = n
        self.conf = conf

    @abstractmethod
    def _get_topo_name(self) -> str:
        pass

    def _get_topo_config(self) -> str:
        topo_config = """\
topology = {topo};
k = {k};
n = {n};

"""
        return topo_config.format(
            topo=self._get_topo_name(),
            k=self.k,
            n=self.n,
        )

    def create_config(self, configs_dir: Path):
        config_path = configs_dir.joinpath("config_" + self.get_topology_name())
        config_content = self._get_topo_config() + self._fill_base_config(self.conf)
        with open(config_path, "w") as file:
            file.write(config_content)
        return config_path

    def get_topology_name(self):
        return f"{self._get_topo_name()}_k{self.k}_n{self.n}" + self.get_indep_namepart(
            self.conf
        )


class MeshConfig(CellTopoConfig):
    def __init__(self, k, n, conf):
        super().__init__(k, n, conf)

    def _get_topo_name(self):
        return "mesh"


class TorusConfig(CellTopoConfig):
    def __init__(self, k, n, conf):
        super().__init__(k, n, conf)

    def _get_topo_name(self):
        return "torus"


def new_cell_config(
    cls,
    num_nodes: int,
    links: str,
    routing_func: str,
    traffic_type: str,
    sim_count: int,
) -> ISimConfig:
    parsed_links = list(map(int, links.split(",")))
    return cls(
        parsed_links[0],
        parsed_links[1],
        TopoIndependentConfig(
            routing_func,
            traffic_type,
            sim_count,
        ),
    )


def new_mesh_config(*args, **kwargs) -> ISimConfig:
    return new_cell_config(MeshConfig, *args, **kwargs)


def new_torus_config(*args, **kwargs) -> ISimConfig:
    return new_cell_config(TorusConfig, *args, **kwargs)
