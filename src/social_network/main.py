import pathlib
import sys

from gunicorn.app.wsgiapp import run


def main() -> None:
    config_path = pathlib.Path(__file__).parent.resolve() / "api" / "gunicorn_conf.py"
    sys.argv = f"gunicorn --access-logfile - --config {config_path} src.social_network.api.app:build_application()".split()
    sys.exit(run())


if __name__ == "__main__":
    main()
