import os
import time

from leapp import reporting
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.common import config
from leapp.libraries.stdlib import CalledProcessError, api, run
from leapp.libraries.common import config


DEFAULT_EXCESSIVE_UPTIME_LIMIT_DAYS = 30
DAY_IN_SECONDS = 24 * 60 * 60
FMT_LIST_SEPARATOR = "\n    - "


def check_excessive_uptime():
    uptime_seconds = _get_uptime()
    EXCESSIVE_UPTIME_LIMIT_DAYS = _get_excessive_uptime_limit_days()
    EXCESSIVE_UPTIME_LIMIT_SECONDS = EXCESSIVE_UPTIME_LIMIT_DAYS * DAY_IN_SECONDS

    if uptime_seconds > EXCESSIVE_UPTIME_LIMIT_SECONDS:
        summary = (
            "This host has not been rebooted for over {} days. "
            "To reduce the risk of boot issues related to any changes made since the last reboot, "
            "policy requires the host to be rebooted before going forward with the upgrade."
        ).format(EXCESSIVE_UPTIME_LIMIT_DAYS)

        report = [
            reporting.Title("Excessive uptime detected"),
            reporting.Summary(summary),
            reporting.Severity(reporting.Severity.HIGH),
            reporting.Groups([reporting.Groups.SANITY, reporting.Groups.INHIBITOR]),
            reporting.Remediation(hint="Please reboot the host machine."),
        ]
        reporting.create_report(report)


def _get_excessive_uptime_limit_days():
    return config.get_env("LEAPP_EXCESSIVE_UPTIME_LIMIT_DAYS", DEFAULT_EXCESSIVE_UPTIME_LIMIT_DAYS)


def _get_uptime():
    """
    Get system uptime in seconds.

    :returns: Uptime in seconds
    :rtype: float
    """
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds


def check_mismatched_kernel_versions():
    running_kernel_version = api.current_actor().configuration.kernel

    # Get default kernel version
    try:
        default_kernel_version = run(["grubby", "--default-kernel"])["stdout"].strip()
        # Remove the /boot/vmlinuz- prefix from the path
        default_kernel_version = os.path.basename(default_kernel_version).split("-", 1)[1]
    except (OSError, CalledProcessError):
        api.current_logger().warning("Failed to query grubby for default kernel", exc_info=True)
        return

    if running_kernel_version != default_kernel_version:
        summary = (
            "This host is running different kernel version ({}) than the default kernel version ({}) configured "
            "in the bootloader. Maybe a new kernel version was installed without then rebooting the host? "
            "Policy requires the host to be rebooted before going forward with the upgrade."
        ).format(running_kernel_version, default_kernel_version)

        kernel_versions_related = [
            reporting.RelatedResource("default_kernel_version", default_kernel_version),
            reporting.RelatedResource("running_kernel_version", running_kernel_version),
        ]

        report = [
            reporting.Title("Mismatched kernel versions detected"),
            reporting.Summary(summary),
            reporting.Severity(reporting.Severity.HIGH),
            reporting.Groups([reporting.Groups.SANITY, reporting.Groups.INHIBITOR]),
            reporting.Remediation(hint="Please reboot the host machine."),
        ] + kernel_versions_related
        reporting.create_report(report)


def check_modified_boot_files():
    boot_files = []
    for root, _, files in os.walk("/boot"):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                boot_files.append(file_path)

    modified_boot_files = []
    uptime_seconds = _get_uptime()
    for file in boot_files:
        if os.stat(file).st_mtime > time.time() - uptime_seconds:
            modified_boot_files.append(file)

    if modified_boot_files:
        sorted_boot_files = sorted(modified_boot_files)
        summary = (
            "Some files on the /boot partition have been modified since the last reboot. "
            "To reduce the risk of boot issues related to changes made since the last reboot, "
            "policy requires the host to be rebooted before going forward with the upgrade."
            "The following files have been modified:{}{}".format(
                FMT_LIST_SEPARATOR, FMT_LIST_SEPARATOR.join(sorted_boot_files)
            )
        )

        boot_files_related = [reporting.RelatedResource("file", f) for f in sorted_boot_files]

        report = [
            reporting.Title("Modified files under /boot detected"),
            reporting.Summary(summary),
            reporting.Severity(reporting.Severity.HIGH),
            reporting.Groups([reporting.Groups.SANITY, reporting.Groups.INHIBITOR]),
            reporting.Remediation(hint="Please reboot the host machine."),
        ] + boot_files_related
        reporting.create_report(report)
