from pprint import pp

import docker
from docker.models.containers import Container
from docker.models.images import Image

from common.terminal import read_terminal


def _extract_port(container: Container):
    ports = container.ports['80/tcp']
    return int(ports[0]['HostPort'])


class ContainersHolder:
    def __init__(self, containers: list[Container]):
        self.port_mapping = {
            _extract_port(cnt): cnt
            for cnt in containers
            if cnt.status == 'running'
        }
        self._id_mapping = {cnt.id: cnt for cnt in containers}

    def get_by_id(self, id_: str) -> Container | None:
        return self._id_mapping.get(id_)


class Client:
    def __init__(self):
        context = read_terminal(
            'docker info | '
            'awk \'/[[:blank:]]*Context/ '
            '{ split($0,a,":"); gsub(/[[:blank:]]/,"",a[2]); print a[2] }\''
        )
        endpoint = read_terminal(
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

    @property
    def containers(self) -> ContainersHolder:
        image = self.image
        containers = self.client.containers.list(all=True, filters={'ancestor': image.id})
        return ContainersHolder(containers)


if __name__ == '__main__':
    pp(Client().containers)
