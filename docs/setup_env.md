# Backlog

The **Backlog** of hackhatons and dev-meetings activities can be found in the [**logs**](./logs) folder.

## Code Contribution and Dev Environment

Instructions to setup the (local) Python development environment are reported below, using either `venv` or `conda` (for Anaconda Python distribution):

- [`venv` virtual environment](#venv)
- [`conda` virtual environment](#conda)

[`black`](https://github.com/python/black) and [`flake8`](https://github.com/PyCQA/flake8) are used for uniform and _PEP8-compliant_ coding style and formatting. Automate checking for style and formatting is integrated via **pre-commit** git hooks. More details in the [**pre-commit**](#precommit) section.

---

<a name="venv"></a>

### `venv` Virtual Environment

The `venv` module provides support for creating lightweight “virtual environments”
with their own site directories, optionally isolated from system site directories.
Each virtual environment has its own Python binary
(which matches the version of the binary that was used to create this environment)
and can have its own independent set of installed Python packages in
its site directories.

**Note**: The `venv` module is part of the **Python Standard Library**, so no further
installation is required.

The following **`3`** steps are required to setup a new virtual environment
using `venv`:

1. Create the environment:

   ```shell script
   python -m venv <PATH-TO-VENV-FOLDER>/thecurious
   ```

2. Activate the environment:

```shell
 source <PATH-TO-VENV-FOLDER>/thecurious/bin/activate
```

3. Install the Required Package (using the `requirements.txt` file):

   ```shell
   pip install -r requirements.txt
   ```

4. (**Optional**) Create new Jupyter notebook Kernel

To avoid re-installing the entire Jupyter stack into the new environment, it is possible to add a new **Jupyter Kernel** to be used in notebooks with the "default" Jupyter.

To do so, please make sure that the `ipykernel` package is installed in the **new** Python environment:

```shell script
pip install ipykernel  ## this should be the default pip
```

Then, execute the following command:

```shell script
python -m ipykernel install --user --prefix <PATH-TO-VENV-FOLDER>/thecurious --display-name "Python 3 (TheCurious)"
```

Further information [here](https://ipython.readthedocs.io/en/stable/install/kernel_install.html)

<a name="conda"> </a>

### `conda` virtual environment

If you are using Anaconda Python distribution (recommended),
it is possible to re-create the virtual (conda) environment using the export `.yml` (`YAML`) file:

```shell script
conda env create -f thecurious_conda_env.yml
```

This will create a new Conda environment named `thecurious` with all the
required packages. To **activate** the environment:

```shell script
conda activate thecurious
```

#### (**Optional**) Create new Jupyter notebook Kernel

To avoid re-installing the entire Jupyter stack into the new environment, it is possible to add a new **Jupyter Kernel** to be used in notebooks with the "default" Jupyter.

To do so, please make sure that the `ipykernel` package is installed in the **new** conda environment:

```shell script
conda install ipykernel
```

Then, still remaining in the **new** conda environment, execute the following command:

```shell script
python -m ipykernel install --user --name thecurious --display-name "Python 3 (TheCurious)"
```

Further information [here](https://ipython.readthedocs.io/en/stable/install/kernel_install.html)

<a name="precommit"></a>

## Pre-commit

In order to automate the `black` and `flake8` code formatting, this project integrates the `pre-commit` Python package.

The `pre-commit` package can be installed via pip
(already **included** in the _virtual environment_):

```shell
pip install pre-commit
```

To install and **enbale** the git hooks (in the `./git/hooks` directory):

```shell
pre-commit install
```

---
