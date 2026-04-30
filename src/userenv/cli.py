import typer

from .userenv import (
    list_,
    create,
    activate,
    active,
    deactivate,
    check_pythonuserbase_equals_userenv_dir,
)

app = typer.Typer()
app.callback()(check_pythonuserbase_equals_userenv_dir)
app.command("list")(list_)
app.command("create")(create)
app.command("activate")(activate)
app.command("active")(active)
app.command("deactivate")(deactivate)


if __name__ == "__main__":
    app()
