# leapp-supplements

This repository contains custom actors for the Leapp project that enable in-place upgrades to the next major version of the Red Hat Enterprise Linux system.
It aims to handle common 3rd party use cases during the upgrade process.

## Table of Contents
- [leapp-supplements](#leapp-supplements)
  - [Table of Contents](#table-of-contents)
  - [Actor list](#actor-list)
  - [Actor description](#actor-description)
    - [CheckRebootHygiene](#checkreboothygiene)
  - [Building the Custom Actors RPM](#building-the-custom-actors-rpm)
    - [Prerequisites](#prerequisites)
    - [Building the RPM](#building-the-rpm)
    - [Installing the RPM](#installing-the-rpm)
    - [Using the Custom Actors](#using-the-custom-actors)
  - [Contributing](#contributing)

## Actor list

The following actors are currently available in this repository:
- checkreboothygiene

These actors are listed in [`actor-list.txt`](./actor-list.txt) file by default.

## Actor description

### CheckRebootHygiene

The CheckRebootHygiene actor will report an inhibitor in case of conditions
that may be prohibited by an organization's reboot hygiene policy.

The actor will report inhibitor risk when:
* The host uptime is greater than the maximum defined by the policy.
* The running kernel version does not match the default kernel version configured in the bootloader.
* Any files are found under /boot that have been modified since the last reboot.

## Building the Custom Actors RPM

In order to bundle the custom actors from this Git repository, follow the instructions below.

### Prerequisites

- A system running Red Hat Enterprise Linux 7 or 8
- `git` installed on your system
- `make` package installed
- `rpm-build` package installed
- Appropriate Python development package

You can install these prerequisites by running the following command:

- On RHEL 7:

    ```bash
    sudo yum install git make rpm-build python2-devel
    ```

- On RHEL 8:

    ```bash
    sudo dnf install git make rpm-build python3-devel
    ```

### Building the RPM

1. Clone the repository to your local machine:
```bash
git clone https://github.com/oamg/leapp-supplements.git
```

2. Change to the `leapp-supplements` directory:
```bash
cd leapp-supplements
```

3. Ensure the `actor-list.txt` file contains the actors you want to bundle. Each actor should be listed on a separate line. Lines starting with `#` are treated as comments and will be ignored. Feel free to add or remove actors as needed for your specific needs.

4. Build the RPM package by running the following command:

- For upgrade between RHEL 7 and RHEL 8:

    ```bash
    make rpmbuild DIST_VERSION=7
    ```

- For upgrade between RHEL 8 and RHEL 9:

    ```bash
    make rpmbuild DIST_VERSION=8
    ```

After the process is complete, you should see the generated RPM files in the current directory.

### Installing the RPM

To install the custom actors RPM, run the following command:
```bash
sudo yum install ./<generated_rpm_file>
```

Replace `<generated_rpm_file>` with the actual RPM file generated in the previous step. Its name should end with `.noarch.rpm`.

### Using the Custom Actors

Once the RPM is installed, the custom actors are automatically integrated with the Leapp project. You can now perform in-place upgrades using the Leapp command-line interface. The custom actors from this repository will be used during the upgrade process. For more details, they can be seen installed under `/usr/share/leapp-repository/custom-repositories/system_upgrade_supplements`.

For more information on using Leapp and performing in-place upgrades, please refer to the [Leapp documentation](https://leapp.readthedocs.io/) and relevant Red Hat documentation regarding RHEL upgrades.

## Contributing

Section containing details about how to contribute to the project.

Before writing any code, familiarize yourself with the [Leapp project documentation](https://leapp.readthedocs.io/en/latest/). The section — [Creating your first actor](https://leapp.readthedocs.io/en/latest/first-actor.html) — is a good place to start.
