import aiohttp
import asyncio
from pyuseragents import random as random_useragent
from loguru import logger
from sys import stderr
from random import choice, randint
from json import load
from os import system
from os.path import exists
from urllib3 import disable_warnings
from multiprocessing.dummy import Pool
from aiohttp_proxy import ProxyConnector
from sys import platform
from msvcrt import getch


with open('countries.json', 'r', encoding='utf-8') as file:
    countries = load(file)


class Wrong_Response(Exception):
    def init(self, message):
        self.message = message


disable_warnings()
def clear(): return system('cls' if platform == "win32" else 'clear')


logger.remove()
logger.add(stderr,
           format="<white>{time:HH:mm:ss}</white> | "
                  "<level>{level: <8}</level> | "
                  "<cyan>{line}</cyan> - "
                  "<white>{message}</white>")


def random_tor_proxy():
    proxy_auth = str(randint(1, 0x7fffffff))\
                 + ':'\
                 + str(randint(1, 0x7fffffff))
    proxies = f'socks5://{proxy_auth}@localhost:' + str(choice(tor_ports))
    return(proxies)


def random_file_proxy():
    with open(proxy_folder, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    proxy_str = f'{proxy_type}://' + choice(lines)

    return(proxy_str)


headers = {
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://nbaallworld.com',
    'referer': 'https://nbaallworld.com/'
}


async def get_connector():
    if use_proxy:
        if proxy_source == 1:
            connector = ProxyConnector.from_url(random_tor_proxy())

        else:
            connector = ProxyConnector.from_url(random_file_proxy())

    else:
        connector = None

    return(connector)


async def main(email):
    try:
        async with aiohttp.ClientSession(headers={
                                                **headers,
                                                'user-agent': random_useragent()
                                            },
                                         connector=await get_connector()) as session:
            async with session.post('https://nbaallworld.com/api/signup',
                                    json={
                                        'dob': f'{randint(1, 12)}/'
                                               f'{randint(1, 28)}/'
                                               f'{randint(1950, 2022)}',
                                        'dobMillis': f'{randint(10000, 99999)}0000000',
                                        'email': email,
                                        'legal-confirm': 'on',
                                        'region': choice(countries
                                                         ['countries']
                                                         ['country'])
                                        ['countryCode'],
                                        'share-data-confirm': 'on'
                                    }) as r:
                if 'success":true,' not in str(await r.text()):
                    raise Wrong_Response(str(await r.text))

    except Wrong_Response as error:
        logger.error(f'{email} | Wrong Response: {error}')

        with open('errors.txt', 'a', encoding='utf-8') as file:
            file.write(f'{email}\n')

    except Exception as error:
        logger.error(f'{email} | Unexpected error: {error}')

        with open('errors.txt', 'a', encoding='utf-8') as file:
            file.write(f'{email}\n')

    else:
        logger.success(f'{email} | The account has been successfully registered')

        with open('registered.txt', 'a', encoding='utf-8') as file:
            file.write(f'{email}\n')

    finally:
        return


def wrapper(email):
    global progress

    asyncio.run(main(email))

    progress += 1
    system('title ' + f'{progress}/{len(emails)}')


if __name__ == '__main__':
    if platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        from ctypes import windll
        windll.kernel32.SetConsoleTitleW('NBA_AllWorld Auto Reger | by NAZAVOD')

    print('Telegram channel - https://t.me/n4z4v0d\n')

    threads = int(input('Threads: '))
    use_proxy = input('Use proxies? (y/N): ').lower()

    if use_proxy == 'y':
        use_proxy = True

        proxy_source = int(input('Proxy Source (1 - tor proxies; '
                                 '2 - from .txt): '))

        if proxy_source == 2:
            proxy_type = input('Enter proxy type (http; https; socks4; socks5): ')
            proxy_folder = input('Drop .txt with proxies: ')

        else:
            if exists('tor_ports.txt'):
                with open('tor_ports.txt', 'r', encoding='utf-8') as file:
                    tor_ports = [row.strip() for row in file]

            else:
                tor_ports = [9150]

    else:
        use_proxy = False

    emails_folder = input('Drop .txt with emails: ')

    with open(emails_folder, 'r', encoding='utf-8') as file:
        emails = [row.strip() for row in file]

    clear()

    progress = 0
    system('title ' + f'{progress}/{len(emails)}')

    with Pool(processes=threads) as executor:
        executor.map(wrapper, emails)

    logger.success('Работа успешно завершена')
    print('\nPress Any Key To Exit..')
    getch()
    exit()
