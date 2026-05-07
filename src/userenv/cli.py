import typer

from .userenv import (
    list_,
    create,
    activate,
    active,
    deactivate,
    setup,
    delete,
    common,
)

app = typer.Typer(
    add_completion=False,
)

app.callback()(common)
app.command("list")(list_)
app.command("create")(create)
app.command("activate")(activate)
app.command("active")(active)
app.command("deactivate")(deactivate)
app.command("setup")(setup)
app.command("delete")(delete)


if __name__ == "__main__":
    app()
