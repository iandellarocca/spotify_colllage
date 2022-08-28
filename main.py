# Built-in modules
import sys
from argparse import ArgumentParser, Namespace
from typing import List
import requests
import asyncio
import aiohttp
from io import BytesIO
from random import choice

# pip installed modules
import numpy as np
from PIL import Image
from jsonpath_ng import parse

# Spotipy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def get_images(urls: List[str]):
    images = []

    async def get_them_then():
        async with aiohttp.ClientSession() as session:
            for url in urls:
                async with session.get(url) as response:
                    image = Image.open(BytesIO(await response.content.read()))
                    images.append(image)

    asyncio.run(get_them_then())
    return images


def main(options: Namespace):
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    results = spotify.playlist_items(options.playlist)

    songs = results['items']
    while results['next']:
        results = spotify.next(results)
        songs.extend(results['items'])

    shape = options.shape
    s = options.image_size
    single_size = dict([(0, (640, 640)), (1, (300, 300)), (2, (64, 64))])[s]

    jsonpath_expr = parse(f'$.track.album.images[{s}].url')
    urls = set()
    attempts = 0
    while len(urls) < shape[0]*shape[1] and attempts < shape[0]*shape[1]*2:
        urls.add(jsonpath_expr.find(choice(songs))[0].value)
        attempts += 1

    if len(urls) < shape[0]*shape[1]:
        sys.exit(-1)

    full_img = np.zeros((shape[0] * single_size[0], shape[1] * single_size[1], 3), dtype='uint8')
    images = get_images(list(urls))
    for i, img in enumerate(images):
        img = np.array(img)
        if len(img.shape) == 2:
            img = img[:, :, np.newaxis]
        row = i // shape[1]
        column = i % shape[1]
        full_img[row * img.shape[0]:(row + 1) * img.shape[0], column * img.shape[1]: (column + 1) * img.shape[1], :] = img

    img = Image.fromarray(full_img)
    img.save('test.png' if options.output is None else options.output)


def parse_args(args: List[str] = None):
    parser = ArgumentParser()

    parser.add_argument('playlist', help='URL of the playlist')
    parser.add_argument('-s', '--shape', nargs=2, default=(4, 4),
                        help="(N, M) Shape of the collage, N rows and M columns.")
    parser.add_argument('-i', '--image-size', default=1,
                        help='Individual artwork size (0: 640x640, 1: 300x300, 2: 64x64)')
    parser.add_argument('-o', '--output', default=None)

    return parser.parse_args(args[1:])


if __name__ == '__main__':
    main(parse_args(sys.argv))
