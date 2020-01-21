from base.terminal import Cli
import os


if __name__ == '__main__':
    ROOT_PATH = os.getcwd()
    cli = Cli(ROOT_PATH)
    try:
        cli.cmdloop()
    except KeyboardInterrupt as e:
        pass
    finally:
        cli.stop_service(None)