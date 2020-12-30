import logging

from pycall import Application, Call, CallFile

# How long to wait for the alarm to answer
# Unfortunately it has to ring 10 times, which is roughly 1 minute.
DEFAULT_WAIT_TIME = 65

# Wait 10 seconds between retries
DEFAULT_RETRY_TIME = 10

# Retry twice
DEFAULT_MAX_RETRIES = 2

# Default user that will own the call files
DEFAULT_ASTERISK_USER = "asterisk"

# Default spool directory
DEFAULT_SPOOL_DIR = "/var/spool/asterisk/outgoing"

# Map relevant actions to DTMF sequences
# See user manual at https://static.interlogix.com/library/466-2266_rev_f.pdf
ACTION_TO_DTMF = {
    "disarm": ["1"],
    "arm_doors_and_windows": ["2"],
    "arm_motion_sensors": ["3"],
    "arm_doors_and_windows_no_delay": ["2", "2"],
    "arm_motion_sensors_with_latchkey": ["3", "3"],
    "arm_doors_and_windows_and_motion_sensors": ["2", "3"],
    "arm_doors_and_windows_with_no_entry_delay_and_motion_sensors_with_latchkey": ["2", "2", "3", "3"],
    "terminate": ["9"],
}

logger = logging.getLogger(__name__)


class Controller:
    """ SimonXT controller class """

    def __init__(
        self,
        access_code: str,
        extension: str,
        wait_time: int = DEFAULT_WAIT_TIME,
        retry_time: int = DEFAULT_RETRY_TIME,
        max_retries: int = DEFAULT_MAX_RETRIES,
        asterisk_user: str = DEFAULT_ASTERISK_USER,
        spool_dir: str = DEFAULT_SPOOL_DIR,
    ) -> None:

        self.access_code = access_code
        self.extension = extension
        self.wait_time = wait_time
        self.retry_time = retry_time
        self.max_retries = max_retries
        self.asterisk_user = asterisk_user
        self.spool_dir = spool_dir

    def _build_dtmf_sequence(self, action: str) -> str:
        """
        Build DTMF tone sequence to send to alarm
        """

        if action not in ACTION_TO_DTMF:
            raise ValueError(f"Invalid action: {action}")

        # "w" means wait a half second
        # For more details, see https://wiki.asterisk.org/wiki/display/AST/Application_SendDTMF

        # Wait before sending the access code
        sections = ["w", self.access_code]

        # Add requested action
        sections.extend(ACTION_TO_DTMF[action])

        # Hang up
        sections.extend(ACTION_TO_DTMF["terminate"])

        # Join all tones with a half-second in between them
        result = "w".join(sections)

        return result

    def send_command(self, action: str) -> None:
        """ Send control sequence via Asterisk call file """

        call = Call(
            f"SIP/{self.extension}", wait_time=self.wait_time, retry_time=self.retry_time, max_retries=self.max_retries
        )

        seq = self._build_dtmf_sequence(action)

        logger.debug("Sending action '%s' (DTMF: '%s') to alarm", action, seq)

        action = Application("SendDTMF", seq)
        c = CallFile(call, action, user=self.asterisk_user, spool_dir=self.spool_dir, archive=True)
        c.spool()

    def disarm(self) -> None:
        """ Disarm """

        self.send_command("disarm")

    def arm_home(self) -> None:
        """ Arm while at home """

        self.send_command("arm_doors_and_windows_no_delay")

    def arm_away(self) -> None:
        """ Arm when going away """

        self.send_command("arm_doors_and_windows_and_motion_sensors")
