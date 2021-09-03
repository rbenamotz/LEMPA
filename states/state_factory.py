from application import Application
from .env_init_state import EnvInit
from .fail_state import FailState
from .firmware_downloader import FirmwareDownload
from .program_state import ProgramState
from .sense_profile_state import SensingProfileState
from .success_state import SuccessState
from .wait_for_button_state import WaitForButtonState
from .fw_erase import FirmwareEraseState
from .exception_state import ExceptionState
from .shutdown_state import ShutDownState


def state_by_code(code, app):
    if (not code):
        return None
    if code == Application.APP_STATE_INIT:
        return EnvInit(app)
    if code == Application.APP_STATE_PROFILE_SENSE:
        return SensingProfileState(app)
    if code == Application.APP_STATE_FIRMWARE_DOWNLOAD:
        return FirmwareDownload(app)
    if code == Application.APP_STATE_WAITING_FOR_BUTTON:
        return WaitForButtonState(app)
    if code == Application.APP_STATE_PROGRAMMING:
        return ProgramState(app)
    if code == Application.APP_STATE_SUCCESS:
        return SuccessState(app)
    if code == Application.APP_STATE_FAIL:
        return FailState(app)
    if code == Application.APP_STATE_ERASE:
        return FirmwareEraseState(app)
    if code == Application.APP_STATE_EXCEPTION:
        return ExceptionState(app)
    if code == Application.APP_STATE_SHUTDOWN:
        return ShutDownState(app)
    raise ValueError("Unknown state %s" % code)
