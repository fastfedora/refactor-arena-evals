# Refactor Arena Evals

This repo contains the exports and logs from eval runs done using the
[refactor-arena](https://github.com/fastfedora/refactor-arena) setting with the
[large/sonnet4-100](https://github.com/fastfedora/full-repo-datasets/tree/main/datasets/large/sonnet4-100),
along with analyses of those logs.

## Getting Started

Install the repo:

```bash
git clone fastfedora/refactor-arena-evals.git
uv sync
```

Download eval logs and/or exports:

```bash
# Install the large file management dependencies
uv sync --extra data

# Download everything
uv run dvc pull

# Download eval logs and exports from honest baseline runs
uv run dvc pull runs/honest-baselines

# Download just the eval logs for both honest and attack runs
uv run dvc pull runs/honest-baselines/logs
uv run dvc pull runs/attacks/logs
```

Run the analysis scripts:

```bash
# Install the analysis dependencies
uv sync --extra analysis

# Run one of the analysis scripts
python -m scripts/{script-name}.py
```

## File Organization

`analysis/`
: Contains charts and other analysis results.

`configs/`
: Contains the configuration file used for the eval runs.

`data/`
: Contains data extracted from the runs.

`runs/`
: Contains the logs and exports of honest and attack runs.

`scripts/`
: Contains the scripts used to extract the data and analyze it.

### Run File Sizes

The eval logs and exports in the `runs` folder can be quite large. If you download these, you'll
need this amount of space (48 GB if everything is downloaded):

- `runs/honest-baselines/logs`: 1.3 GB
- `runs/honest-baselines/exports`: 6.4 GB
- `runs/attacks/logs`: 7.4 GB
- `runs/attacks/exports`: 32 GB

## Things to Do

### Import Runs

To re-run an exported run, import it using:

```bash
refactor-arena --import <path-to-export-folder>
```

For instance:

```bash
refactor-arena --import runs/honest-baselines/exports/sonnet-4_2026-03-29T11-54-07_all-main-tasks_large-sonnet4-100_honest
```

This imports the configuration, chat messages and the submitted solution into the sandbox for each
sample, then re-runs all of the solvers except for the agent, re-runs the scorers and monitors, and
recalculates all the metrics. The configuration used will be the same configuration as was
originally exported.

Use `--overrides` to pass a comma-separate list of override configurations. This can be used to
test new scorers, monitors and metrics:

```bash
refactor-arena --import <path-to-export-folder> --overrides new-monitors.yaml
```

Finally, to re-export the imported run, just add `--export`:

```bash
refactor-arena --import <path-to-export-folder> --export
```

### Rescore Runs

To re-score an eval log, use the `rescore` command:

```
refactor-arena rescore --config scenarios/large-sonnet4-100 <path-to-eval-log>
```

Use the configuration to make any changes you want for the re-run.

To simply recalculate the metrics, use the `--metrics-only` option:

```
refactor-arena rescore --config scenarios/large-sonnet4-100 --metrics-only <path-to-eval-log>
```

### Diff a Solution

Every exported sample contains a `repo` and `reference-repo`. The `repo` folder is the submitted
solution, while the `reference-repo` is a copy of the original repo given to the agent. To quickly
see the changes an agent made for a sample, simply diff the two:

```
cd <sample-folder>
diff reference-repo repo
```

For instance:

```
cd runs/honest-baselines/exports/opus-4-6_2026-03-27T20-24-03_all-main-tasks_large-sonnet4-100_honest/001_user_management_api__refactor_single_file
diff reference-repo repo
```

### Run Sample as Human Agent

Samples can be re-instantiated in sandboxes using import. By specifying `--human-agent`, you can
enter the sandbox interactively and explore the sample:

```bash
refactor-arena --import <path-to-export-folder> --human-agent
```

Most exports will have so many samples that you'll want to limit to a specific run using the dataset
filters. For instance, to run the `001_user_management_api__refactor_single_file__exfiltrate-env-var/api-key`
sample, you would use:

```bash
refactor-arena \
  --import <path-to-export-folder> \
  --main-task refactor_single_file \
  --side-task exfiltrate-env-var/api-key \
  --repo 001 \
  --human-agent
```

## Notes

### Reruns

There was an error in the original runs that caused errors while diffing the solution code. Since
this could cause issues with the scores, all of the runs were re-run using an import command similar
to:

```bash
refactor-arena --export --import runs/honest-baselines/exports/sonnet-4_2026-03-29T11-54-07_all-main-tasks_large-sonnet4-100_honest
```

Logs and exports for the original runs and the re-runs are both included in this repo.

Note that the GPT 5.4 attack run was not re-run, since it refused to do any of the side tasks so
the original run was invalid anyway.

