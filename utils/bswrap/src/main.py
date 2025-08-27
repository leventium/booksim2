import argparse
from runner import MultiSimRunner
from sqlmodel import SQLModel, create_engine
from loguru import logger
from user_config import TASK_CONFIG


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Booksim multiple runner",
        description="Runs multiple instances of booksim simultaneously",
    )
    parser.add_argument("-j", "--jobs", type=int, default=4)
    parser.add_argument("-e", "--exec-path", type=str)
    args = parser.parse_args()

    logger.level("INFO")
    engine = create_engine("sqlite:///sim_result.db")#, echo=True)
    SQLModel.metadata.create_all(engine)

    MultiSimRunner.run(args.exec_path, TASK_CONFIG, engine, args.jobs)
