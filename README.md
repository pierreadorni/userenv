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

Install the latest development version directly from the github repo:
```
git clone git@github.com:pierreadorni/userenv.git
cd userenv
pip install .
```
Configure the environment variables in your shell configuration file (e.g., .bashrc, .zshrc)
```bash
export USERENV_DIR="$HOME/.userenv" # default value, adapt to your needs
export PYTHONUSERBASE="$USERENV_DIR"
export PATH="$PATH:$USERENV_DIR/bin"
```
then reload your config
``` bash
source ~/.bashrc # example for .bashrc
```

You're good to go !

```
userenv --help
                                                                                                    
 Usage: userenv [OPTIONS] COMMAND [ARGS]...                                                         
                                                                                                    
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                          │
│ --show-completion             Show completion for the current shell, to copy it or customize the │
│                               installation.                                                      │
│ --help                        Show this message and exit.                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
│ list                                                                                             │
│ create                                                                                           │
│ activate                                                                                         │
│ active                                                                                           │
│ deactivate                                                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Contributing

Feel free to submit pull requests and file bugs in the issue tracker.