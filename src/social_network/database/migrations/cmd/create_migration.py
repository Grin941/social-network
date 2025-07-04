import argparse
import logging
import sys

import alembic.config
from alembic import command

from social_network.database.migrations.cmd.const import INI_FILEPATH

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)

logger = logging.getLogger(__name__)


def _parse_args(argv: list[str]) -> str:
    parser = argparse.ArgumentParser(description="Create migration")

    migration = parser.add_argument_group("migration")
    migration.add_argument(
        "--message",
        dest="message",
        default="",
        type=str,
    )

    cli_args = parser.parse_args(argv)

    return cli_args.message


def main() -> None:
    alembic_cfg = alembic.config.Config(file_=INI_FILEPATH)
    command.revision(
        alembic_cfg,
        message=_parse_args(sys.argv[1:]),
        autogenerate=True,
    )


if __name__ == "__main__":
    main()
