import shutil
import argparse
from pathlib import Path
from runner import MultiSimRunner
from sqlmodel import SQLModel, create_engine
from loguru import logger
from user_config import TASK_CONFIG


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="bswrap",
        description="Booksim multiple runner: Runs multiple "
        "instances of booksim simultaneously",
    )
    parser.add_argument("-e", "--exec-path", type=str, required=True,
                        help="Path to the BookSim simulator executable.")
    parser.add_argument("-j", "--jobs", type=int, default=1,
                        help="Number of jobs running simulation tasks. "
                        "Recomended to be equal to number of "
                        "physical CPUs. [Default: 1]")
    parser.add_argument("-d", "--configs-directory", type=str,
                        default="configs", help="Path to the directory "
                        "where simulation configs are stored. "
                        "[Default: 'configs']")
    args = parser.parse_args()

    configs_dir = Path(args.configs_directory).absolute()
    if configs_dir.exists():
        shutil.rmtree(configs_dir)
    configs_dir.mkdir()

    logger.level("INFO")
    engine = create_engine("sqlite:///sim_result.db")#, echo=True)
    SQLModel.metadata.create_all(engine)

    MultiSimRunner.run(
        Path(args.exec_path).absolute(),
        TASK_CONFIG,
        configs_dir,
        engine,
        args.jobs,
    )
