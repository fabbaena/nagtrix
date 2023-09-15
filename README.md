# Nagtrix

Nagtrix is a cli python module that retrieves session usage, logon duration, application usage, and application failures while yielding an output appropriate for a Nagios plugin.

The following Citrix Monitoring API OData objects are queried for the aforementioned purposes:

- `Sessions` (`python -m nagtrix session --help` for usage)
- `SessionActivitySummaries` (`python -m nagtrix sessionactivitysummary --help` for usage)
- `ApplicationActivitySummaries` (`python -m nagtrix applicationactivitysummary --help` for usage)
- `FailureLogSummaries` (`python -m nagtrix recentfailurelogsummaries --help` for usage)

These cli commands are currently designed to work with OData V2. Make sure to have Nagios Core and Nagios Plugins installed before attempting to install the custom plugins of this repository.

Install Python 3.10 or higher. Make sure it is linked to `python3` amd that `pip` is installed for this version.

## Installing the Python Module
### Through a Release File
Next, you can install the python module found in this repository. If there is a release file available, download it and run `pip install <downloaded file>` in order to install the module.

### Through a Build
Make sure you have the latest version of `build` before you build a release file by running `python3 -m pip install --upgrade build`. Then, build the source code by running `python3 -m build` in the root directory of this repository. After this runs successfully, any one of the files in the `dist` folder that appears can be used to install the module using `pip install <a file in dist>`.

## Usage

There are currently 4 commands defined for Natrix. Information on their names can be displayed by simply running 
```bash
python -m nagtrix --help
```

To display information about a particular command's arguments, simply add a `--help` after the command. For example, to display the arguments for the `session` command run:
```bash
python -m nagtrix session --help
```