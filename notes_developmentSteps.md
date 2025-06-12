# Dev Notes (Jun - Jul 2025)

## Setup

### Local

```bash
conda env create -f environment.yml
conda activate libraryname-dev
pip install -e .[dev]
jupyter lab
```

- for any dependency updates: update environment.yml first, then update the conda env using this updated yml, then reinstall the library
conda env update -f environment.yml
pip install -e . --upgrade

### steps to begin dev
- activate conda env
- install library in editable mode using pip

Step 5: Iterative development

    Modify your library code inside the pyspoc/ folder (or wherever your package lives).

    The notebook sees changes instantly (because of editable install).

---

* **Conda environment** manages most dependencies (like numpy, torch, scikit-learn).
* `pip install -e .` installs your local library + any leftover dependencies pip handles (or new ones you add only in pyproject.toml).
