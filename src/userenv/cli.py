import typer

from .userenv import (
    list_,
    create,
    activate,
    active,
    deactivate,
    setup,
    common,
    check_pythonuserbase_equals_userenv_dir,
)

app = typer.Typer(
    add_completion=False,
)
app.callback()(check_pythonuserbase_equals_userenv_dir)
app.callback()(common)
app.command("list")(list_)
app.command("create")(create)
app.command("activate")(activate)
app.command("active")(active)
app.command("deactivate")(deactivate)
app.command("setup")(setup)


if __name__ == "__main__":
    app()
