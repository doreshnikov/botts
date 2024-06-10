import argparse
import json
import time

import docker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog='Invoker startup script'
)
parser.add_argument('ports')
parser.add_argument('--rebuild', action='store_true')
parser.add_argument('--no-clean', action='store_true')

args = parser.parse_args()
if ':' not in args.ports or len(args.ports.split(':')) != 2:
    print('Should specify ports in format <low:high>')
    exit(1)
ports = args.ports.split(':')
if not ports[0].isnumeric() or not ports[1].isnumeric():
    print('Ports should be integer numbers')
    exit(1)
low, high = map(int, ports)
if low < 65000 or high < low:
    print('Ports should satisfy 65000 <= low <= high')
    exit(1)

LABEL = 'invoker'
TAG = '0.1gamma'
INVOKER = 'invoker_mp.py'

logger.info('Setting up Docker client...')
client = docker.client.from_env()
logger.info(f'> done, {client.info()["ID"]}')

images = client.images.list(all=True, filters={'label': 'service=invoker'})
if len(images) == 0 and not args.rebuild:
    logger.critical('No images with label \'invoker\' found')
    exit(1)
image = images[0] if len(images) > 0 else None
logger.info(f'Initial image image: {image}')

if not args.no_clean and image is not None:
    containers = client.containers.list(all=True, filters={'ancestor': image.id})
    logger.info(f'Containers to clean: {len(containers)}')
    for container in containers:
        logger.info(f'> {container}...')
        container.remove(force=True)
        logger.info('> done')

if args.rebuild:
    logger.info('Re-building invoker image...')
    image = client.images.build(
        path='.', tag=f'{LABEL}:{TAG}',
        rm=True
    )[0]
    logger.info(f'> done, {image}')
    logger.info('Removing dangling images...')
    for dangling_image in client.images.list(all=True, filters={'dangling': True}):
        logger.info(f'> {dangling_image}...')
        dangling_image.remove(force=True)
    logger.info(f'> done')

invokers = {}
for port in range(low, high + 1):
    logger.info(f'Creating container on port {port}...')
    cnt = client.containers.create(
        f'{LABEL}:{TAG}',
        ports={f'{port}/tcp': f'{port}'},
        tty=True, detach=True,
        command=f'{INVOKER} {port}'
    )
    logger.info(f'> done, {cnt}')
    invokers[port] = cnt.id
    cnt.start()

    logger.info(f'Started, waiting for availability')
    while b'Bind successful' not in cnt.logs():
        logger.info('> sleeping for 1s')
        time.sleep(1)
    logger.info('> done')

with open('invokers.json', 'w') as config_file:
    invokers = {
        'remote': invokers,
        'basic': 2
    }
    json.dump(invokers, config_file, indent=2)
