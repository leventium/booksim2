from itertools import product

from model import Config, Topology
from simulation_task import SimulationTask


class ConfigGenerator:
    @staticmethod
    def generate_configs(tasks: list[SimulationTask]) -> list[Config]:
        res: list[Config] = []

        for task in tasks:
            topos: list[Topology] = []

            for args in product(task.topo_names, task.num_nodes, task.links):
                topos.append(
                    Topology(
                        name=args[0],
                        num_nodes=args[1],
                        args=args[2],
                    )
                )

            for args in product(
                topos, task.routing_funcs, task.traffic_types, task.sim_counts
            ):
                res.append(
                    Config(
                        topo=args[0],
                        routing_function=args[1],
                        traffic_type=args[2],
                        sim_count=args[3],
                    )
                )

        return res
