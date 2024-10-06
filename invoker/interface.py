from pprint import pp
from subprocess import Popen, PIPE

import docker
from docker.models.containers import Container
from docker.models.images import Image


def _read_terminal(cmd: str) -> str:
    p = Popen(cmd, stdout=PIPE, shell=True)
    return p.stdout.read().decode('utf-8').strip()


class Client:
    def __init__(self):
        context = _read_terminal(
            'docker info | '
            'awk \'/[[:blank:]]*Context/ '
            '{ split($0,a,":"); gsub(/[[:blank:]]/,"",a[2]); print a[2] }\''
        )
        endpoint = _read_terminal(
            'docker context ls | '
            f'awk \'$1=="{context}" '
            '{ for(i=1;i<=NF;i++) { if($i~/.*\\.sock/) { print $i } } }\''
        )

        self.client = docker.DockerClient(base_url=endpoint)
        self.service = 'invoker'

        with open('invoker/Dockerfile') as df:
            dockerfile = df.readlines()
        for line in dockerfile:
            if not line.startswith('LABEL service'):
                continue
            self.service = line.split('=')[1].strip().strip('"')
            break

    @property
    def image(self) -> Image:
        images = self.client.images.list(all=True, filters={'label': f'service={self.service}'})
        return images[0]

    @staticmethod
    def _extract_port(container: Container):
        ports = container.ports['80/tcp']
        return int(ports[0]['HostPort'])

    @property
    def containers(self) -> dict[int, Container]:
        image = self.image
        containers = self.client.containers.list(all=True, filters={'ancestor': image.id})
        return {
            self._extract_port(container): container
            for container in containers
        }


if __name__ == '__main__':
    pp(Client().containers)
