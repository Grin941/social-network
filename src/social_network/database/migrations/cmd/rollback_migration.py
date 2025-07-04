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


def main() -> None:
    command.downgrade(alembic.config.Config(file_=INI_FILEPATH), "-1")


if __name__ == "__main__":
    main()
