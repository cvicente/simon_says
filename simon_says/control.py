import logging
from pathlib import Path

from pycall import Application, Call, CallFile

from simon_says.config import ConfigLoader

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
        config_path: Path = None,
        access_code: str = None,
        extension: str = None,
        wait_time: int = None,
        retry_time: int = None,
        max_retries: int = None,
        asterisk_user: str = None,
        spool_dir: Path = None,
    ) -> None:
        self.cfg = ConfigLoader(config_path).config if config_path else ConfigLoader().config
        self._state_db_key = "armed_state"
        self.access_code = access_code or self.cfg.get("control", "access_code")
        self.extension = extension or self.cfg.get("control", "extension")
        self.wait_time = wait_time or int(self.cfg.get("control", "wait_time"))
        self.retry_time = retry_time or int(self.cfg.get("control", "retry_time"))
        self.max_retries = max_retries or int(self.cfg.get("control", "max_retries"))
        self.asterisk_user = asterisk_user or self.cfg.get("control", "asterisk_user")
        self.spool_dir = spool_dir or Path(self.cfg.get("control", "spool_dir"))

        if not self.spool_dir.is_dir():
            raise ValueError(f"spool_dir {self.spool_dir} is not a valid directory")

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

        callfile_args = {"archive": True, "spool_dir": self.spool_dir}
        if self.asterisk_user:
            callfile_args["user"] = self.asterisk_user

        c = CallFile(call, action, **callfile_args)
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
