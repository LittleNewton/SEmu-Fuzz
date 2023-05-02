# SEmu-Fuzz

SEmu-Fuzz is a fuzzing extension of SEmu. It was developed as part of our paper ["What Your Firmware Tells You Is Not How You Should Emulate It: A Specification-Guided Approach for Firmware Emulation"](https://doi.org/10.1145/3548606.3559386) at CCS 2022. SEmu-Fuzz is based on [Unicorn Engine](https://github.com/unicorn-engine/unicorn) as ISA emulator and intergrate [AFL](https://github.com/shandianchengzi/afl-unicorn) or [AFLplusplus](https://github.com/AFLplusplus/AFLplusplus) as the fuzzing engine. Taking advantage of Unicorn API, we could sync all peripheral access (mmio and dma r/w) to with SEmu peripheral model. SEmu peripheral model is used to check, execute and chain the [extracted condition-action rules](https://github.com/MCUSec/SEmu) at runtime.

## Citing our paper

```bibtex
@inproceedings{SEmu,
  title={What Your Firmware Tells You Is Not How You Should Emulate It: A Specification-Guided Approach for Firmware Emulation},
  author={Zhou, Wei and Zhang, Lan and Guan, Le and Liu, Peng and Zhang, Yuqing},
  booktitle={Proceedings of the 2022 ACM SIGSAC Conference on Computer and Communications Security},
  pages={3269--3283},
  year={2022}
}
```

## Directory structure of the repo

```bash
├── LICENSE
├── README.md
├── docs/                              # More documentation about quick_start and configuration
├── semu_fuzz
│   ├── __init__.py
│   ├── configuration
│   │   ├── args.py                    # Command-line argument parser
│   │   └── config.py                  # Configuration file parser
│   ├── emulate
│   │   ├── native/                    # Shared library generated by building the native library
│   │   ├── nvic.py                    # Python code for handling interrupt vector table
│   │   ├── semu
│   │   │   ├── class_def.py           # Class definitions for SEmu peripheral model
│   │   │   └── rule.py                # Code for SEmu peripheral model synthetization
│   │   └── uc.py                      # Code for emulating microcontroller
│   ├── fuzz
│   │   └── fuzz.py                    # Code for conducting fuzzing
│   ├── helper
│   │   ├── configs                    # Base configuration file (Now only support ARM Cortex-M)
│   │   ├── dump_launch.py             # Code for dumping vscode launch configuration
│   │   ├── dump_semu_config.py        # Code for dumping SEmu emulation configuration
│   │   ├── stat_bb_coverage.py        # Code for generating basic block coverage statistics
│   │   ├── stat_draw_bb_img.py        # Code for generating basic block coverage images
│   │   └── main.py                    # Main entry point for the semu-fuzz-helper
│   ├── log
│   │   ├── debug.py                   # Code for debug-level logging
│   │   ├── fuzz_stat.py               # Code for logging fuzzing statistics
│   │   └── log.py                     # Code for generic logging
│   ├── exit.py                        # Code for handling exit conditions
│   ├── globs.py                       # Global variables used in the package
│   ├── utils.py                       # Shared functions used in the package
│   └── harness.py                     # Main entry point for the semu-fuzz
└── setup.py                           # Setup script for the package
```

## installation

**Note:** If you meet "Core dump" when installation, use `pip freeze` to determine your dependency.

### Docker Installation (Recommend)

The installation of AFL/AFLplusplus will fuzz your local unicorn environment, so Docker is recommended.

1. Use `ubuntu_install_docker.sh` to install docker command.
2. Build docker by `dockerfile`, run:

    ```
    ./build_docker.sh
    ```

3. Run docker in bash:
    ```
    ./run_docker.sh
    ```
4. Start to use `semu-fuzz` and `semu-fuzz-helper`!

### Local Installation

The dependency of `SEmu-Fuzz` is very minimal, and it can be installed directly on your local machine. All you need to do is install it using `pip` and choose your preferred `AFL`.

We also provide a script which covers installation.

Just run (Recommended Python > 3.6):

```bash
./install_local.sh
```

This script has 3 functions:
1. Create a virtual environment named `semu`;
2. Add command `semu-fuzz` and `semu-fuzz-helper` for use.
3. Install [AFLplusplus](https://github.com/AFLplusplus/AFLplusplus).

When you need raw [AFL](https://github.com/shandianchengzi/afl-unicorn), just change the link and dirname in [install_local.sh#L30-L31](./install_local.sh#L30-L31), and run it again.

**Note:** the original AFL has many issues, such as mistaking `semu-fuzz` as a shell script, making it impossible to perform fuzzing tests. To address this issue, we also provide a [modified AFL](https://github.com/shandianchengzi/afl-unicorn) with some configuration changes.

If you don't need AFL, please just use `pip` to install:

```bash
cd </pathto/SEmu-Fuzz>
pip install .
```

## Usage

After installing this package, two command line instructions, `semu-fuzz` and `semu-fuzz-helper`, will be added. For specific usage instructions, add the `-h` parameter.

Note: If you install this package in virtualenv, please run `workon semu` before use.

### semu-fuzz

```bash
usage: semu-fuzz [-h] [-s] [-d DEBUG_LEVEL] [-l INSTR_LIMIT] input_file config_file
```

You can use `semu-fuzz -h` for the details.

`semu-fuzz` is a command-line tool designed for fuzz testing that utilizes the SEmu peripheral model to simulate the execution of mutated input files. The tool requires two positional arguments: `input_file` and `config_file`, which specify the path to the mutated input file and the configuration file of the test case for emulation, respectively.

For more information about the configuration file, please refer to the [docs/configuration.md](docs/configuration.md).

In addition to the required arguments, `semu-fuzz` provides several optional arguments that can be used to customize the behavior of the tool. These include:

- `-h` or `--help`: Displays the help message and exits
- `-s` or `--stat`: Enables recording of new blocks created by the input file
- `-d DEBUG_LEVEL` or `--debug_level DEBUG_LEVEL`: Specifies the level of debug information printed during execution, with a range of 0 (disables debug) to 3 (maximum debug)
- `-l INSTR_LIMIT` or `--instr-limit INSTR_LIMIT`: Specifies the maximum number of instructions to execute. The default is 30,000,000, and setting the limit to 0 disables it.

### semu-fuzz-helper

```bash
usage: semu-fuzz-helper [-h] [-a] [-s] [-t DURATION] {config,launch,stat} base_configs
```

You can use `semu-fuzz-helper -h` for the details.

`semu-fuzz-helper` is a command-line utility that provides additional functionality to `semu-fuzz`. The tool allows users to configure and launch fuzzing campaigns, as well as collect bb coverage statistics on the performance of these campaigns.

This tool has four helper functions which can be selected using the positional argument.

- `config`: This helper function is used to dump semu configuration for testcases.
- `launch`: This helper function is used to dump VSCode launch configurations for testcases.
- `stat`: This helper function is used to gather basic block coverage statistics and generate an image for testcases.
- `run`: This helper function is used to run afl test of testcases with nohup.

All of these helper need `base_configs` as input argument. `base_configs` is a yml file, which takes simplest settings of firmware. For more information about this configuration file, please refer to the [docs/configuration.md](docs/configuration.md).

Options:

- `-h`, `--help`: Displays the help message and exits
- `-a`, `--afl`: Just for helper launch. If set, enable the dumping of vscode launch with AFL.
- `-s`, `--syms`: Just for helper config. If set, enable symbols table extract. (This arg is not recommended. Recommend using ida_dump_symbols.py to dump syms)
- `-t DURATION`, `--duration DURATION`: Just for helper stat. The duration of AFL execution, the default value is 24, which means 24 hours.

## Simple Demo

This repository provides a simple test case that you can use to verify the proper installation of `semu-fuzz` and `semu-fuzz-helper`, and test their basic functionality. If you want to re-run our experiments, you can replace this testcase and configuration file with our [unit-test](https://github.com/MCUSec/SEmu/tree/main/DataSet/p2im-unit-tests) and [fuzzing-test](https://github.com/MCUSec/SEmu/tree/main/DataSet/fuzz_tests) simples.

1. Use `semu-fuzz` to debug with debug level 3:
    ```bash
    semu-fuzz samples/base_inputs/sample1.bin samples/semu_config.yml -d 3
    ```
    If the execution is successful, you will see the debugging information in the `samples/debug_output` directory.

2. Use `semu-fuzz-helper` to generate a vscode launch file:
    ```bash
    semu-fuzz-helper launch samples/base_configs.yml
    ```
    If the execution is successful, you will see a new `launch.json` file generated in the `samples/` directory.

## More documentation

1. [quick_start.md](docs/quick_start.md): This documentation explains how to quickly use this tool for **our fuzz tests**, how to use the tool to **test your own testcases** and **draw BB coverage images**.
2. [configuration.md](docs/configuration.md): This document describes the composition of **the configuration file for testcases** and how to **generate batch configuration files**.
3. [debug_in_vscode.md](docs/debug_in_vscode.md): This documentation explains how to **debug in vscode** and how to **generate batch vscode launch files of testcases**.

## Issues
If you encounter any problems while using our tool, please open an issue.
