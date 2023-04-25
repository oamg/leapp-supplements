from leapp.actors import Actor
from leapp.libraries.actor import checkreboothygiene
from leapp.reporting import Report
# from leapp.tags import ChecksPhaseTag
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag
from leapp.models import InstalledRedHatSignedRPM


class CheckRebootHygiene(Actor):
    """
    The CheckRebootHygiene actor will report an inhibitor in case of conditions
    that may be prohibited by an organization's reboot hygiene policy.

    The actor will report inhibitor risk when:
    * The host uptime is greater than the maximum defined by the policy.
    * The running kernel version does not match the default kernel version
      configured in the bootloader.
    * Any files are found under /boot that have been modified since the last reboot.
    """

    name = "check_reboot_hygiene"
    consumes = ()
    produces = (Report,)
    tags = (ChecksPhaseTag,)

    def process(self):
        self.log.info("Checking reboot hygiene")
        self.log.info("Checking for excessive uptime")
        checkreboothygiene.check_excessive_uptime()
        self.log.info("Checking for mismatched kernel versions")
        checkreboothygiene.check_mismatched_kernel_versions()
        self.log.info("Checking for modified boot files")
        checkreboothygiene.check_modified_boot_files()
        self.log.info("Reboot hygiene check complete")
