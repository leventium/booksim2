from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from dataclasses import dataclass
from itertools import product
from model import Topology, Config, Result
from simulator import SimRunner, BadSimSummary, SimSummaryNotFound
from sqlmodel import Session
from sqlalchemy import Engine
from loguru import logger
from tqdm import tqdm


@dataclass
class ProgressBarSync:
    bar: tqdm
    mx: Lock


@dataclass
class SimulationTask:
    topo_names: list[str]
    num_nodes: list[int]
    links: list[int]

    routing_funcs: list[str]
    traffic_types: list[str]
    sim_counts: list[int]


class MultiSimRunner:
    @staticmethod
    def _generate_configs(tasks: list[SimulationTask]) -> list[Config]:
        res: list[Config] = []

        for task in tasks:
            topos: list[Topology] = []

            for args in product(task.topo_names, task.num_nodes, task.links):
                topos.append(Topology(
                    name=args[0],
                    num_nodes=args[1],
                    links=args[2],
                ))
            
            for args in product(topos, task.routing_funcs,
                                task.traffic_types, task.sim_counts):
                res.append(Config(
                    topo=args[0],
                    routing_function=args[1],
                    traffic_type=args[2],
                    sim_count=args[3],
                ))

        return res

    @staticmethod
    def _worker(cfg: Config, simulator: SimRunner, cfgs_dir: Path,
                sync_bar: ProgressBarSync) -> Result | None:
        with sync_bar.mx:
            sync_bar.bar.set_description(
                f"Processing '{cfg.topo.name}_N{cfg.topo.num_nodes}_"
                f"R{cfg.routing_function}'"
            )
            sync_bar.bar.update()

        try:
            return simulator.sim(cfg, cfgs_dir)
        except (BadSimSummary, SimSummaryNotFound):
            logger.error(f"Error occured on config {cfg}")

        return None

    @staticmethod
    def run(simulator_path: Path, tasks: list[SimulationTask],
            configs_dir: Path, engine: Engine, jobs: int):
        logger.info("Preparing configurations.")
        configs = MultiSimRunner._generate_configs(tasks)

        logger.info("Registering configs.")
        with Session(engine) as sess:
            for cfg in configs:
                sess.add(cfg)
            sess.commit()
            for cfg in configs:
                sess.refresh(cfg)
                tmp = cfg.topo

        logger.info("Starting simulations.")
        sync_bar = ProgressBarSync(tqdm(total=len(configs)), Lock())
        simulator = SimRunner(simulator_path)

        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = pool.map(
                lambda cfg: MultiSimRunner._worker(
                    cfg,
                    simulator,
                    configs_dir,
                    sync_bar),
                configs
            )

            with Session(engine) as sess:
                for res in results:
                    if res is not None:
                        sess.add(res)
                sess.commit()

        sync_bar.bar.close()
