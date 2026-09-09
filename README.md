# aiida-mace

AiiDA plugin to run [MACE](https://github.com/ACEsuit/mace) trainings. It provides a
calculation, a parser and a work chain built on top of the generic training engine of
[aiida-trains-pot](https://github.com/aiida-trieste-developers/aiida-trains-pot)
(`aiida_trainspot`).

## Requirements

- `aiida-core >= 2.6.2, < 3`
- `aiida-trainspot >= 2.0.0`
- `ase == 3.29.0`
- MACE installed on the target computer, with the `mace_run_train`, `mace_prepare_data` and
  `mace_create_lammps_model` executables configured as AiiDA codes.

## Installation

```bash
pip install .
```

## Entry points

| Entry point | Class                  | Type        |
| ----------- | ---------------------- | ----------- |
| `mace`      | `MaceTrainCalculation` | Calculation |
| `mace`      | `MaceBaseParser`       | Parser      |
| `mace.base` | `MaceTrainWorkChain`   | Work chain  |

## Calculation

`MaceTrainCalculation` writes the MACE configuration file, runs the training and then runs the
postprocessing code to export the models. The run name is forced to `aiida`, since all output and
checkpoint filenames expected by the parser derive from it.

Main inputs, in addition to those of the base `TrainCalculation`
(`training_set`, `validation_set`, `test_set`, `checkpoints`, `postprocess_code`, `restart`):

- `mace_config` (`Dict`): MACE configuration. The keys controlling dataset paths, seed, name and
  the energy/forces/stress labels are overwritten by the plugin.
- `parent_folder` (`RemoteData`, optional): remote folder of a previous training. Datasets and
  checkpoints are symlinked instead of being uploaded again. It must be on the same computer as
  the code.
- `do_preprocess` (`Bool`, default `False`) and `preprocess_code` (`Code`): run
  `mace_prepare_data` before the training and use the resulting HDF5 datasets.
- `protocol` (`Str`, optional): `naive-finetune` or `replay-finetune`. Both require
  `finetune_model`; `replay-finetune` also requires `finetune_replay_dataset` and enables
  multihead finetuning.

Datasets are written as extended XYZ with the `dft_energy`, `dft_forces` and `dft_stress` keys.
If `E0s` is not given in `mace_config`, it is taken from the training set, falling back to
`average` when the reference energies are not available.

Outputs: `model_stage1_*` and `model_stage2_*` (`pytorch`, `ase`, `lammps` and, when produced,
`mliap`), `checkpoints`, `RMSE` and `results`.

Exit codes: `410` preprocessing failed, `420` training failed, `430` postprocessing failed, plus
the `300` and `400` codes of the base class.

## Work chain

`MaceTrainWorkChain` extends `TrainWorkChain` and handles restarts. When a calculation runs out
of walltime it is restarted from the remote folder of the previous run, so datasets and
checkpoints already present on the remote computer are reused.
