"""Fail-closed framing shared by the prospective cohort launcher and controls."""
import re


def valid_frame(qemu_exit, serial, reason=None):
    text = serial.replace(b'\r\n', b'\n').decode(errors='replace')
    exits = re.findall(r'^__ECPP_CHILD_EXIT__ (\d+) timeout=(\d+)$', text, re.M)
    begin = '__ECPP_GUEST_BEGIN__\n'
    done = '__ECPP_GUEST_COMPLETE__\n'
    return (qemu_exit == 33 and reason is None and len(exits) == 1 and exits[0][1] == '0'
            and text.count(begin) == text.count(done) == 1
            and text.count('__ECPP_INIT_ABI__ 4 4 4\n') == 1
            and text.index(begin) < text.index('__ECPP_CHILD_EXIT__') < text.index(done))
