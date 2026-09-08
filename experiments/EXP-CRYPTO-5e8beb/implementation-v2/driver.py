"""Unavailable scientific launcher. No binding can enable execution here.

No file inspection, approval authentication, lock acquisition, transport,
backend selection, or scientific imports are implemented. Presence or hashes
of user-supplied files would not establish any of those permissions.
"""
import json


class ScientificLaunchUnavailable(RuntimeError):
    """This version cannot launch science, regardless of supplied bindings."""


REFUSAL = ('Scientific launch unavailable: this zero-run correction provides '
           'no admission authentication or scientific execution path.')


def check_launch_admission(binding=None, **kwargs):
    """Always raise, without inspecting or trusting any binding."""
    raise ScientificLaunchUnavailable(REFUSAL)


def launch_scientific(binding=None, **kwargs):
    """Always raise; no run allocation, file writes or backend calls."""
    raise ScientificLaunchUnavailable(REFUSAL)


def main(argv=None):
    """Every CLI invocation refuses with exit 3, including empty/malformed args."""
    print(json.dumps({'status': 'scientific_launch_unavailable',
                      'scientific_runs': 0, 'reason': REFUSAL}, sort_keys=True))
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
