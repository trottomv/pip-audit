"""
Command-line entrypoints for `pip-audit`.
"""

import argparse
import enum
import logging
import os

from pip_audit.audit import AuditOptions, Auditor
from pip_audit.dependency_source import PipSource
from pip_audit.format import ColumnsFormat, JsonFormat, VulnerabilityFormat
from pip_audit.service import OsvService, VulnerabilityService
from pip_audit.util import assert_never

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PIP_AUDIT_LOGLEVEL", "INFO").upper())


@enum.unique
class OutputFormatChoice(str, enum.Enum):
    """
    Output formats supported by the `pip-audit` CLI.
    """

    Columns = "columns"
    Json = "json"

    def to_format(self) -> VulnerabilityFormat:
        if self is OutputFormatChoice.Columns:
            return ColumnsFormat()
        elif self is OutputFormatChoice.Json:
            return JsonFormat()
        else:
            assert_never(self)

    def __str__(self):
        return self.value


@enum.unique
class VulnerabilityServiceChoice(str, enum.Enum):
    """
    Python vulnerability services supported by `pip-audit`.
    """

    Osv = "osv"
    Pypi = "pypi"

    def to_service(self) -> VulnerabilityService:
        if self is VulnerabilityServiceChoice.Osv:
            return OsvService()
        elif self is VulnerabilityServiceChoice.Pypi:
            raise NotImplementedError
        else:
            assert_never(self)

    def __str__(self):
        return self.value


def audit():
    """
    The primary entrypoint for `pip-audit`.
    """
    parser = argparse.ArgumentParser(
        description="audit the Python environment for dependencies with known vulnerabilities",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--requirement",
        type=argparse.FileType("r"),
        action="append",
        default=[],
        dest="requirements",
        help="audit the given requirements file; this option can be used multiple times",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=OutputFormatChoice,
        choices=OutputFormatChoice,
        default=OutputFormatChoice.Columns,
        help="the format to emit audit results in",
    )
    parser.add_argument(
        "-s",
        "--vulnerability-service",
        type=VulnerabilityServiceChoice,
        choices=VulnerabilityServiceChoice,
        default=VulnerabilityServiceChoice.Osv,
        help="the vulnerability service to audit dependencies against",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="collect all dependencies but do not perform the auditing step",
    )

    args = parser.parse_args()
    logger.debug(f"parsed arguments: {args}")

    if args.requirements:
        raise NotImplementedError

    service = args.vulnerability_service.to_service()
    formatter = args.format.to_format()

    source = PipSource()
    auditor = Auditor(service, options=AuditOptions(dry_run=args.dry_run))

    print(formatter.format(auditor.audit(source)))