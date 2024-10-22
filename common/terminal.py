from subprocess import Popen, PIPE


def read_terminal(cmd: str) -> str:
    p = Popen(cmd, stdout=PIPE, shell=True)
    return p.stdout.read().decode('utf-8').strip()


# Having some problems with this one
def host_ip() -> str:
    return read_terminal(
        'cat /etc/hosts | '
        'grep host.docker.internal | '
        'awk \'{print $1}\''
    )
