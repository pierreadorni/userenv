# UserEnv: User Installed Modules Manager

Do you work on a system where python environments are pre-configured, and your only way to add custom modules is using `pip install --user` ? UserEnv allows you to keep multiple sets of user packages in a single python environment, as **user environments**. 

## A Concrete Example

Let's say you need to use both NumPy-1 and NumPy-2 in the same environment. First, create a *userenv* for NumPy-1:
```bash
$ userenv create numpy1 && userenv activate numpy1
User environment 'numpy1' created at /home/adorni/.userenv/envs/numpy1.
User environment 'numpy1' activated.

$ pip install --user numpy==1.26.4
...
Successfully installed numpy-1.26.4
```

Then, create a *userenv* for NumPy 2:
```bash
$ userenv create numpy2 && userenv activate numpy2
User environment 'numpy2' created at /home/adorni/.userenv/envs/numpy2.
User environment 'numpy2' activated.

$ pip install --user numpy==2.4.4
...
Successfully installed numpy-2.4.4
```

Et voilà ! You can now use both versions of numpy the same way you would use a normal *venv*:
```bash
$ userenv activate numpy1 && python -c "import numpy; print(numpy.__version__)"
User environment 'numpy1' activated.
1.26.4

$ userenv activate numpy2 && python -c "import numpy; print(numpy.__version__)"
User environment 'numpy2' activated.
2.4.4
```

## Installation


```bash
$ pip install --user pyuserenv
$ userenv setup
```

**Make sure** to follow the setup instructions with the modifications to your shell configuration file (e.g., .bashrc, .zshrc), then reload your config
``` bash
source ~/.bashrc # example for .bashrc
```

You're good to go !

```
$ userenv --help

 Usage: userenv [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────╮
│ --version  -v        Show the version of pyuserenv                │
│ --help               Show this message and exit.                  │
╰───────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────╮
│ list        List all user environments with their installed       │
│             module count and last installed module datetime.      │
│ create      Create a new user environment.                        │
│ activate    Activate a user environment.                          │
│ active      Display the currently active user environment.        │
│ deactivate  Deactivate the currently active user environment.     │
│ setup       Setup the user environment directory structure.       │
│ delete      Delete an existing user environment.                  │
╰───────────────────────────────────────────────────────────────────╯
```

## Contributing

Feel free to submit pull requests and file bugs in the issue tracker.