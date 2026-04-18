set dotenv-load

_default:
  @ just --list --unsorted


# -----------------------------------------------------------------------------
# Refactor Arena
# -----------------------------------------------------------------------------
# Run a scenario
[group: 'Setting']
run scenario *args:
  refactor-arena --config scenarios/{{scenario}}.yaml {{args}}

# Run a scenario in honest mode
[group: 'Setting']
run-honest scenario *args:
  refactor-arena --config scenarios/{{scenario}}.yaml --eval-mode honest {{args}}

# Run a scenario in attack mode
[group: 'Setting']
run-attack scenario *args:
  refactor-arena --config scenarios/{{scenario}}.yaml --eval-mode attack {{args}}


# -----------------------------------------------------------------------------
# Virtual Environment
# -----------------------------------------------------------------------------
# Initialize the virtual environment
[group: 'Virtual Environment']
init:
  uv venv --python 3.12 .venv

# Sync core dependencies and install the package in editable mode
[group: 'Virtual Environment']
sync:
  uv sync

# Sync all dependencies and install the package in editable mode
[group: 'Virtual Environment']
sync-all:
  uv sync --extra analysis,data


# -----------------------------------------------------------------------------
# Large File Management
# -----------------------------------------------------------------------------
# Initialize the management of large files via DVC
[group: 'Large File Management']
init-files:
  uv run dvc init

# Add a large file to be managed
[group: 'Large File Management']
add-files path:
  uv run dvc add {{path}}

# Pull the large files from the remote storage
[group: 'Large File Management']
pull-files args="":
  uv run dvc pull {{args}}

# Push the large files to the remote storage
[group: 'Large File Management']
push-files args="":
  uv run dvc push {{args}}

# List the files on the remote storage
[group: 'Large File Management']
list-remote-files:
  uv run dvc remote list


# -----------------------------------------------------------------------------
# Dependency Management
# -----------------------------------------------------------------------------
# Add dependency
[group: 'Dependencies']
add target:
  uv add {{target}}

# Upgrade dependency
[group: 'Dependencies']
upgrade target:
  uv lock --upgrade-package {{target}} && uv sync

# Remove dependency
[group: 'Dependencies']
remove target:
  uv remove {{target}}

# Show outdated dependencies
[group: 'Dependencies']
outdated:
  uv tree --outdated --depth=1

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
# Clean up testing and build artifacts
[group: 'Utilities']
clean:
  find . -type f -name "*.pyc" -delete
  find . -type d -name "__pycache__" -delete
  rm -rf build/
  rm -rf dist/
  rm -rf *.egg-info/
