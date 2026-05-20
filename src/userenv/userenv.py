from typing_extensions import Annotated
from typing import Optional
import os
import sys
from pathlib import Path
import datetime
import shutil

import typer
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

console = Console()


def get_userenv_dir():
    home_dir = Path.home()
    userenv_dir = home_dir / ".userenv"
    if "USERENV_DIR" in os.environ:
        userenv_dir = Path(os.environ["USERENV_DIR"])

    os.makedirs(userenv_dir, exist_ok=True)

    return userenv_dir


def get_pythonuserbase_dir():
    home_dir = Path.home()
    default_pythonuserbase_dir = home_dir / ".local"
    if "PYTHONUSERBASE" in os.environ:
        return Path(os.environ["PYTHONUSERBASE"])
    else:
        return default_pythonuserbase_dir


def check_userenv_dir_defined():
    if "USERENV_DIR" not in os.environ and sys.argv[1] != "setup":
        console.print(
            Panel(
                f"""[red]Warning:[/red] USERENV_DIR environment variable is not defined. Please run 'userenv setup' and follow the instructions.""",
                highlight=True,
            )
        )


def get_active_userenv():
    if "PYTHONUSERBASE" not in os.environ:
        return None
    pythonuserbase = Path(os.environ["PYTHONUSERBASE"])
    userenv_name = pythonuserbase.name

    userenv_dir = get_userenv_dir()
    userenv_list = os.listdir(userenv_dir / "envs")
    if userenv_name not in userenv_list:
        return None

    return userenv_name


def get_count_installed_modules(env_name: str):
    lib_path = get_userenv_dir() / "envs" / env_name / "lib"

    if not lib_path.exists():
        return 0

    total = 0
    for python_version in lib_path.iterdir():
        total += len(list((python_version / "site-packages").iterdir()))
    return total


def get_last_installed_module_datetime(env_name: str):
    lib_path = get_userenv_dir() / "envs" / env_name / "lib"

    if not lib_path.exists():
        return None

    latest_time = None
    for python_version in lib_path.iterdir():
        site_packages = python_version / "site-packages"
        if site_packages.exists():
            for module in site_packages.iterdir():
                mtime = module.stat().st_mtime
                if latest_time is None or mtime > latest_time:
                    latest_time = mtime

    return (
        datetime.datetime.fromtimestamp(latest_time).strftime("%Y-%m-%d %H:%M")
        if latest_time is not None
        else None
    )


def list_():
    """
    List all user environments with their installed module count and last installed module datetime.
    """
    envs_dir = get_userenv_dir() / "envs"
    os.makedirs(envs_dir, exist_ok=True)
    envs = os.listdir(envs_dir)
    if len(envs) == 0:
        console.print(
            "No user environments found. Use 'userenv create <name>' to create one."
        )
        return

    active_env = get_active_userenv()

    table = Table(min_width=20)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Installed", style="magenta")
    table.add_column("Last Installed", style="green")
    for env in envs:
        last_installed_time = get_last_installed_module_datetime(env)
        table.add_row(
            env if env != active_env else f"[bold cyan]{env} (active)[/bold cyan]",
            str(get_count_installed_modules(env)),
            str(last_installed_time) if last_installed_time is not None else "N/A",
        )

    console.print(table)


def create(
    name: Annotated[
        str, typer.Argument(help="The name of the user environment to create")
    ],
):
    """Create a new user environment."""
    env_path = get_userenv_dir() / "envs" / name

    if os.path.exists(env_path):
        console.print(f"User environment '{name}' already exists.")
        return

    os.makedirs(env_path)

    console.print(f"User environment '{name}' created at {env_path}.")


def delete(
    name: Annotated[
        str, typer.Argument(help="The name of the user environment to delete")
    ],
):
    """Delete an existing user environment."""
    env_path = get_userenv_dir() / "envs" / name

    if not os.path.exists(env_path):
        console.print(f"User environment '{name}' does not exist.")
        return

    # check if the environment to delete is the active one, and if so deactivate it first
    active_env = get_active_userenv()
    if active_env == name:
        deactivate()

    # delete the environment
    shutil.rmtree(env_path)
    console.print(f"User environment '{name}' deleted.")


def activate(
    name: Annotated[
        str, typer.Argument(help="The name of the user environment to activate")
    ],
):
    """Activate a user environment."""
    userenv_dir = get_userenv_dir()
    env_path = userenv_dir / "envs" / name

    if not os.path.exists(env_path):
        console.print(f"User environment '{name}' does not exist.")
        return

    # deactivate the currently active environment, if any
    active_env = get_active_userenv()

    # link the userenv script bin and the userenv lib to the newly activated environment,
    # so that the userenv cli is still reachable
    # bin
    script_path = Path(sys.argv[0]).resolve()
    env_binaries_path = env_path / "bin"
    os.makedirs(env_binaries_path, exist_ok=True)
    userenv_bin_script_path = env_path / "bin" / script_path.name
    if userenv_bin_script_path.is_symlink() or userenv_bin_script_path.exists():
        userenv_bin_script_path.unlink()
    os.symlink(script_path, userenv_bin_script_path)

    # lib
    lib_path = Path(__file__).resolve().parent
    python_version_target = lib_path.parent.name

    new_userenv_site_packages_path = (
        env_path / "lib" / python_version_target / "site-packages"
    )

    os.makedirs(new_userenv_site_packages_path, exist_ok=True)

    if (new_userenv_site_packages_path / "pyuserenv").is_symlink():
        (new_userenv_site_packages_path / "pyuserenv").unlink()
    os.symlink(
        lib_path,
        new_userenv_site_packages_path / "pyuserenv",
    )

    # set pythonuserbase to the selected environment
    command = f"""export PYTHONUSERBASE={env_path}"""
    path = os.environ.get("PATH")
    if (
        active_env is not None
        and path is not None
        and str(userenv_dir / "envs" / active_env / "bin") in path
    ):
        # if there is an active environment, remove it from the path
        path = ":".join(
            [
                p
                for p in path.split(":")
                if p != str(userenv_dir / "envs" / active_env / "bin")
            ]
        )
        command += f""" && export PATH="{path}" """
        command += f""" && echo "User environment '{active_env}' deactivated." """

    if path is not None and not str(env_path / "bin") in path:
        command += f""" && export PATH="$PATH:{env_path / "bin"}" """

    command += f""" && echo "User environment '{name}' activated." """

    print(command)


def active():
    """Display the currently active user environment."""
    active_env = get_active_userenv()
    if active_env is None:
        console.print("No active user environment.")
    else:
        console.print(
            f"[cyan]{active_env}[/cyan] ({get_count_installed_modules(active_env)} installed)"
        )


def deactivate():
    """Deactivate the currently active user environment."""
    if get_active_userenv() is None:
        print("echo 'No active user environment to deactivate.'")
        return
    env_path = get_pythonuserbase_dir()

    command = """export PYTHONUSERBASE=$__pythonuserbase_memory"""
    path = os.environ.get("PATH")
    if path is not None:
        path = ":".join([p for p in path.split(":") if p != str(env_path / "bin")])
        command += f""" && export PATH="{path}" """
    command += f""" && echo "User environment '{env_path.name}' deactivated." """

    print(command)


def setup(
    path: Annotated[
        Optional[Path],
        typer.Argument(
            help="The path to set up pyuserenv in. defaults to a new .userenv directory sibling of the current PYTHONUSERBASE"
        ),
    ] = None,
):
    """Setup the user environment directory structure."""

    # check the setup is not already done
    if os.environ.get("USERENV_DIR") is not None:
        console.print("USERENV_DIR is already set, it seems the setup is already done.")
        return

    pythonuserbase_dir = get_pythonuserbase_dir()
    console.print(f"Current PYTHONUSERBASE: {pythonuserbase_dir}")
    if path is not None:
        userenv_dir = path
    else:
        userenv_dir = pythonuserbase_dir.parent / ".userenv"
    console.print(f"Setting up userenv at {userenv_dir}")

    os.makedirs(userenv_dir, exist_ok=True)
    os.makedirs(userenv_dir / "envs", exist_ok=True)

    rc_code = f"""# pyuserenv setup
export USERENV_DIR={userenv_dir}
export USERENV_BIN={Path(sys.argv[0]).resolve()}
__pythonuserbase_memory="$PYTHONUSERBASE"
userenv() {{
    \\local cmd="${{1-m__missing__}}"
    case "$cmd" in
        activate|deactivate)
            \\eval $("$USERENV_BIN" "$@")
            ;;
        *)
            "$USERENV_BIN" "$@"
    esac    
}}
"""
    console.print(
        Panel(
            f"""Add the following lines to your shell configuration file (e.g. .bashrc, .zshrc) to complete the setup:""",
            expand=False,
            border_style="red",
        )
    )
    console.print(f"[blue]{rc_code}[/blue]")


def version_callback(version: bool = False):
    """Display the version of pyuserenv, dynamically fetched from the package."""
    if not version:
        return

    import importlib.metadata

    ver = importlib.metadata.version("pyuserenv")
    console.print(f"pyuserenv version: {ver}")
    sys.exit(0)


def common(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show the version of pyuserenv",
            is_eager=True,
            show_default=False,
            callback=version_callback,
        ),
    ] = False,
):
    check_userenv_dir_defined()
