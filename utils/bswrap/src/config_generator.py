from collections.abc import Sequence
from itertools import product

from model import Config
from simulation_task import SimulationTask, SimulationTaskLegacy
from topology import Topology


class ConfigGenerator:
    @staticmethod
    def _get_topo_permutation(task: SimulationTaskLegacy) -> list[Topology]:
        return [
            Topology(name, num_nodes, args)
            for name, num_nodes, args in product(
                task.topo_names, task.num_nodes, task.links
            )
        ]

    @staticmethod
    def generate_configs(
        tasks: Sequence[SimulationTask | SimulationTaskLegacy],
    ) -> list[Config]:
        res: list[Config] = []

        for task in tasks:
            topo_list = (
                task.topo
                if isinstance(task, SimulationTask)
                else ConfigGenerator._get_topo_permutation(task)
            )
            res.extend(
                [
                    Config(
                        topo=topo,
                        routing_function=route_func,
                        traffic_type=traffic,
                        sim_count=sim_count,
                    )
                    for topo, route_func, traffic, sim_count in product(
                        topo_list,
                        task.routing_funcs,
                        task.traffic_types,
                        task.sim_counts,
                    )
                ]
            )

        return res
