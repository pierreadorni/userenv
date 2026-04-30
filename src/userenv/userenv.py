from typing_extensions import Annotated
import os
from pathlib import Path
import datetime

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


def check_pythonuserbase_equals_userenv_dir():
    pythonuserbase = get_pythonuserbase_dir()
    userenv_dir = get_userenv_dir()
    if pythonuserbase != userenv_dir:
        console.print(
            Panel(
                f"""[red]Warning:[/red] PYTHONUSERBASE is set to '{pythonuserbase}', which does not match the [italic]userenv[/italic] directory '{userenv_dir}'. This prevents python from accessing packages installed in your activated [italic]userenv[/italic]. Please add the following lines to your shell configuration file (e.g., .bashrc, .zshrc):
[blue]
export USERENV_DIR="$HOME/.userenv" # example path, adjust if needed
export PYTHONUSERBASE="$USERENV_DIR"
export PATH="$USERENV_DIR/bin:$PATH"[/blue]""",
                highlight=True,
            )
        )


def get_active_userenv():
    userenv_dir = get_userenv_dir()
    if not userenv_dir.exists():
        return None
    lib_dir = userenv_dir / "lib"

    if not lib_dir.is_symlink():
        return None

    target = lib_dir.resolve()
    env_name = target.parent.name

    return env_name


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

    # create a symlink from userenv_dir/[lib,bin] to env_path/[lib,bin]
    lib_path = env_path / "lib"
    bin_path = env_path / "bin"
    userenv_lib_path = userenv_dir / "lib"
    userenv_bin_path = userenv_dir / "bin"

    os.makedirs(lib_path, exist_ok=True)
    os.makedirs(bin_path, exist_ok=True)

    if userenv_lib_path.is_symlink() or userenv_lib_path.exists():
        userenv_lib_path.unlink()
    if userenv_bin_path.is_symlink() or userenv_bin_path.exists():
        userenv_bin_path.unlink()

    os.symlink(lib_path, userenv_lib_path)
    os.symlink(bin_path, userenv_bin_path)

    console.print(f"User environment '{name}' activated.")


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
    userenv_dir = get_userenv_dir()
    userenv_lib_path = userenv_dir / "lib"
    userenv_bin_path = userenv_dir / "bin"

    if userenv_lib_path.is_symlink() or userenv_lib_path.exists():
        userenv_lib_path.unlink()
    if userenv_bin_path.is_symlink() or userenv_bin_path.exists():
        userenv_bin_path.unlink()

    console.print("User environment deactivated.")
