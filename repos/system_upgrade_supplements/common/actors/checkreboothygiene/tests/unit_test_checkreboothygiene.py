import os
import time

import mock
import pytest
from leapp import reporting
from leapp.libraries.actor import checkreboothygiene
from leapp.libraries.actor.checkreboothygiene import EXCESSIVE_UPTIME_LIMIT_SECONDS
from leapp.libraries.common.testutils import create_report_mocked, CurrentActorMocked
from leapp.utils.report import is_inhibitor
from leapp.libraries.stdlib import api

KERNEL_VERSION_1 = "3.10.0-1062.1.2.el7.x86_64"
KERNEL_VERSION_2 = "3.10.0-1160.88.1.el7.x86_64"


def assert_inhibitor(should_inhibit):
    if should_inhibit:
        reporting.create_report.called
        assert is_inhibitor(reporting.create_report.report_fields)
    else:
        assert not reporting.create_report.called


@pytest.mark.parametrize(
    "uptime, inhibit",
    (
        (0, False),
        (EXCESSIVE_UPTIME_LIMIT_SECONDS, False),
        (EXCESSIVE_UPTIME_LIMIT_SECONDS + 1, True),
    ),
)
def test_excessive_uptime(uptime, inhibit, monkeypatch):
    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(checkreboothygiene, "_get_uptime", lambda: uptime)
    checkreboothygiene.check_excessive_uptime()
    assert_inhibitor(inhibit)


@pytest.mark.parametrize(
    "booted_kernel, default_kernel, inhibit",
    (
        (KERNEL_VERSION_1, KERNEL_VERSION_1, False),
        (KERNEL_VERSION_1, KERNEL_VERSION_2, True),
    ),
)
def test_mismatched_kernel_versions(booted_kernel, default_kernel, inhibit, monkeypatch):
    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(api, "current_actor", CurrentActorMocked(kernel=booted_kernel))
    monkeypatch.setattr(checkreboothygiene, "run", lambda _: {"stdout": "/boot/vmlinuz-" + default_kernel})
    checkreboothygiene.check_mismatched_kernel_versions()
    assert_inhibitor(inhibit)


@pytest.mark.parametrize(
    "uptime_seconds, since_modified_seconds, inhibit",
    (
        (0, 1, False),
        (0, 3600, False),
        (3600, 0, True),
        (3601, 3600, True),
    ),
)
def test_modified_boot_files(uptime_seconds, since_modified_seconds, inhibit, monkeypatch):
    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(os, "walk", lambda _: [("/boot", [], ["file1", "file2"])])
    monkeypatch.setattr(os.path, "isfile", lambda _: True)

    monkeypatch.setattr(checkreboothygiene, "_get_uptime", lambda: uptime_seconds)
    with mock.patch("os.stat") as mocked_stat:
        mocked_stat.return_value.st_mtime = time.time() - since_modified_seconds
        checkreboothygiene.check_modified_boot_files()

    assert_inhibitor(inhibit)
