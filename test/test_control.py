

def test_build_dtmf(test_controller):
    dtmf = test_controller._build_dtmf_sequence("arm_doors_and_windows_no_delay")
    assert dtmf == "ww1234w2w2w9"


def test_send_disarm_command(test_controller, tmp_path):
    test_controller.send_command("disarm")
    call_file = next(tmp_path.iterdir())
    lines = call_file.read_text().splitlines()
    assert lines[0] == "Channel: SIP/100"
    assert lines[1] == "WaitTime: 65"
    assert lines[2] == "RetryTime: 10"
    assert lines[3] == "Maxretries: 2"
    assert lines[4] == "Application: SendDTMF"
    assert lines[5] == "Data: ww1234w1w9"
    assert lines[6] == "Archive: yes"
    call_file.unlink()


def test_arm_doors_and_windows_no_delay(test_controller, tmp_path):
    test_controller.send_command("arm_doors_and_windows_no_delay")
    call_file = next(tmp_path.iterdir())
    lines = call_file.read_text().splitlines()
    assert lines[5] == "Data: ww1234w2w2w9"
    call_file.unlink()
