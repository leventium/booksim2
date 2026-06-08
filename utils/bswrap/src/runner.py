from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from loguru import logger
from tqdm import tqdm

from config_generator import ConfigGenerator
from model import Config, IResultRepo, Result
from simulation_task import SimulationTask, SimulationTaskLegacy
from simulator import BadSimSummary, SimRunner, SimSummaryNotFound


@dataclass
class ProgressBarSync:
    bar: tqdm
    mx: Lock


class MultiSimRunner:
    @staticmethod
    def _worker(
        cfg: Config, simulator: SimRunner, cfgs_dir: Path, sync_bar: ProgressBarSync
    ) -> Result | None:
        if cfg.topo is None:
            raise ValueError("Topology must be specified in config.")

        with sync_bar.mx:
            sync_bar.bar.set_description(f"Processing {cfg.get_description()}")
            sync_bar.bar.update()

        try:
            return simulator.sim(cfg, cfgs_dir)
        except (BadSimSummary, SimSummaryNotFound):
            logger.warning(f"Error occured on config {cfg}")
        except ValueError:
            logger.warning(f"Error on circulant config: {cfg.topo}")

        return None

    @staticmethod
    def run(
        simulator_path: Path,
        tasks: Sequence[SimulationTask | SimulationTaskLegacy],
        configs_dir: Path,
        repo: IResultRepo,
        jobs: int,
    ):
        logger.info("Preparing configurations.")
        configs = ConfigGenerator.generate_configs(tasks)

        logger.info("Starting simulations.")
        sync_bar = ProgressBarSync(tqdm(total=len(configs)), Lock())
        simulator = SimRunner(simulator_path)

        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = pool.map(
                lambda cfg: MultiSimRunner._worker(
                    cfg, simulator, configs_dir, sync_bar
                ),
                configs,
            )

            for res in results:
                if res is not None:
                    repo.save(res)

        sync_bar.bar.close()
        logger.info("Done.")
