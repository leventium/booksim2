import shutil
import argparse
from pathlib import Path
from runner import MultiSimRunner
from loguru import logger
from model import CSVResultRepo
from user_config import TASK_CONFIG


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="bswrap",
        description="Booksim multiple runner: Runs multiple "
        "instances of booksim simultaneously",
    )
    parser.add_argument("-e", "--exec-path", type=Path, required=True,
                        help="Path to the BookSim simulator executable.")
    parser.add_argument("-j", "--jobs", type=int, default=1,
                        help="Number of jobs running simulation tasks. "
                        "Recomended to be equal to number of "
                        "physical CPUs. [Default: 1]")
    parser.add_argument("-d", "--configs-directory", type=Path,
                        default="tmp", help="Path to the directory "
                        "where simulation configs are stored. "
                        "[Default: 'tmp']")
    parser.add_argument("-o", "--output", type=Path, default="result.csv",
                        help="Name of the output file."
                        "[Default: 'result.csv']")
    args = parser.parse_args()

    configs_dir = args.configs_directory.absolute()
    if configs_dir.exists():
        shutil.rmtree(configs_dir)
    configs_dir.mkdir()

    logger.level("INFO")
    repo = CSVResultRepo(args.output.absolute())

    MultiSimRunner.run(
        args.exec_path.absolute(),
        TASK_CONFIG,
        configs_dir,
        repo,
        args.jobs,
    )

    repo.close()
