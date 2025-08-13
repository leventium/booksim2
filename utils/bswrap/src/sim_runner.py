#!/usr/bin/env python3
import argparse
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from itertools import product
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import subprocess as sp
from tqdm import tqdm

from circulant_builder import Circulant


class RoutingFunc(StrEnum):
    min = "min"
    dor = "dor"
    dim_order = "dim_order"


class TrafficType(StrEnum):
    uniform = "uniform"
    bitcomp = "bitcomp"
    bitrev = "bitrev"
    shuffle = "shuffle"
    transpose = "transpose"
    tornado = "tornado"
    neighbor = "neighbor"
    randperm = "randperm"


@dataclass
class TopoIndependentConfig:
    routing_func: RoutingFunc
    traffic: TrafficType
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
            sim_count=conf.sim_count
        )
    
    def get_indep_namepart(self, conf: TopoIndependentConfig):
        return f"_F{conf.routing_func}_T{conf.traffic}_S{conf.sim_count}"

    @abstractmethod
    def create_config(self) -> str:
        """
        Creates config in filesystem and returns its name.
        """
        pass

    @abstractmethod
    def get_topology_name(self) -> str:
        pass


class CirculantConfig(ISimConfig):
    topo_config = """\
topology = anynet;
network_file = {anynet_filename};

"""
    def __init__(self, num_nodes: int, links: list[int],
                 config: TopoIndependentConfig):
        self.circulant = Circulant(num_nodes, links)
        self.num_nodes = num_nodes
        self.links = links
        self.config = config

    def get_topology_name(self) -> str:
        res = f"circulant_c{self.num_nodes}"
        for link in self.links:
            res += f"_{link}"
        return res + self.get_indep_namepart(self.config)

    def create_config(self):
        config_filename = "config_" + self.get_topology_name()
        topology_filename = "topo_" + self.get_topology_name()

        config_content = self.topo_config.format(
            anynet_filename=topology_filename,
        ) + self._fill_base_config(self.config)
        with open(topology_filename, "w") as file:
            file.write(self.circulant.serialize_booksim())
        with open(config_filename, "w") as file:
            file.write(config_content)

        return config_filename


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

    def create_config(self):
        config_name = "config_" + self.get_topology_name()
        config_content = self._get_topo_config() + self._fill_base_config(self.conf)
        with open(config_name, "w") as file:
            file.write(config_content)
        return config_name

    def get_topology_name(self):
        return (f"{self._get_topo_name()}_k{self.k}_n{self.n}"
                + self.get_indep_namepart(self.conf))


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


class SimRunner:
    def __init__(self, booksim_exec: str):
        self.exec = booksim_exec[2:] if booksim_exec.startswith("./") else booksim_exec

    def sim(self, config: ISimConfig) -> sp.CompletedProcess: # TODO: SimResult must be returned
        return sp.run(
            f"./{self.exec} {config.create_config()} 2>&1",
            shell=True,
            capture_output=True,
        )


def generate_configs() -> list[ISimConfig]:
    indep_confs = []
    for args in product(list(RoutingFunc), list(TrafficType), [1]):
        indep_confs.append(TopoIndependentConfig(*args))

    # cnt = 0
    # confs = Queue()
    confs = []
    for args in product(range(2, 17), [2], indep_confs):
        confs.append(MeshConfig(*args))
        confs.append(TorusConfig(*args))
        # cnt += 2
    for args in product(range(2, 12), [3], indep_confs):
        confs.append(MeshConfig(*args))
        confs.append(TorusConfig(*args))
        # cnt += 2

    circulant_links = [[2**i for i in range(0, j, 2)] for j in range(1, 11, 2)]
    for args in product(range(4, 2000, 50), circulant_links, indep_confs):
        try:
            c = CirculantConfig(*args)
        except ValueError:
            continue
        confs.append(c)
        # cnt += 1
    
    return confs


@dataclass
class ProgressBarSync:
    bar: tqdm
    mx: Lock


def worker(exec_path: str, task: ISimConfig, bar: ProgressBarSync):
    sim = SimRunner(exec_path).sim(task)
    with bar.mx:
        bar.bar.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Booksim massive runner",
        description="Runs multiple instances of booksim simultaneously",
    )
    parser.add_argument("-j", "--jobs", type=int, default=4)
    parser.add_argument("-e", "--exec-path", type=str)
    args = parser.parse_args()

    print("Preparing configurations...")
    tasks = generate_configs() # TODO: FIX
    print("Starting simulations...")
    # bar = ProgressBarSync(tqdm(total=len(tasks)), Lock())
    bar = tqdm(total=len(tasks))
    # threads: list[Thread] = []

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        sim_results = pool.map(
            lambda task: SimRunner(args.exec_path).sim(task), # TODO: add tqdm bar
            tasks,
        )

    for sim_res in sim_results:
        pass

    # for _ in range(args.jobs):
    #     t = Thread(target=worker, args=(args.exec_path, tasks, bar))
    #     t.start()
    #     threads.append(t)

    # tasks.join()
    # for t in threads:
    #     t.join()

    bar.bar.close()
