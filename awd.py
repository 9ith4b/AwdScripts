#!/usr/bin/env python3
#-*- coding: utf-8 -*-


import os
import requests
import logging
import importlib
import datetime
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed


# --------------------------- config -----------------------------


submit_url  = "http://127.0.0.1/submit_flag"
token       = "zRKUNRd8QygFRQEHUn4H7ch21N3KPTuG"
round_num   = 100
round_time  = 0.1   # minutes

LOG         = 1     # turn on log flag




# -------------------------------------------------------------------

logging.basicConfig(format="[*] %(levelname)-8s : %(message)s", level=logging.DEBUG)

EXP_MODULE_DIR  = "core"
FLAG_FILE       = "flags"

INFC = "\033[1;36;40m"
ERRC = "\033[01;37;41m"
WRNC = "\033[1;33;40m"
MSGC = "\033[1;32;40m"
ENDC = "\033[0m"



pinfo    = lambda x : print(INFC + x + ENDC)
winfo    = lambda x : print(WRNC + x + ENDC)

lcerror  = lambda x : logging.error(ERRC + x + ENDC)
lcinfo   = lambda x : logging.info(INFC + x + ENDC)
lcwarn   = lambda x : logging.warning(WRNC + x + ENDC)
lcmsg    = lambda x : logging.info(MSGC + x + ENDC)
linfo    = lambda x : logging.info(x)

def load_modules(root_path=EXP_MODULE_DIR):
    modules = []
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            if not filename.startswith("__") and filename.endswith(".py"):
                # file_path = os.path.join(root, filename)
                file_path = root_path + os.sep + filename
                # print(file_path)
                file_path_noext = file_path.rpartition(".py")[0]
                module_name = file_path_noext.replace(os.sep, ".")
                # print(module_name)
                modules.append(importlib.import_module(module_name))
    return modules

def b2a(bd):
    if isinstance(bd, bytes):
        return bd.decode()
    return bd

def logflag_into_file(flagfile, d):
    d = b2a(d)
    log_file = open(flagfile, "a+")
    log_file.write(d+"\n")
    log_file.close()

class AWD(object):
    timeout = 3.0
    header  = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    exps    = load_modules()
    inter   = 1.0

    def __init__(self, submit_url, token, round_num, round_time):
        self.token      = token
        self.url        = submit_url
        self.round_num  = round_num
        self.round_time = round_time*60     # minutes
    
    def submitflags(self):
        # call exp.getflag
        def getflag(exp):
            if hasattr(exp, "getflag"):
                try:
                    return getattr(exp, "getflag")()
                except Exception as e:
                    lcwarn("oops! " + exp.name + ": " + str(e))
            
        with ThreadPoolExecutor(3) as pool:
            tasks = { pool.submit(getflag, exp): exp for exp in self.exps }
        
        for f in as_completed(tasks):
            flag = f.result()
            lcmsg(f"{tasks[f].name}, flag: {flag}")
            if flag:
                self.submitflag(flag)
                if LOG:
                    logflag_into_file(FLAG_FILE, flag)
            else:
                lcerror("get flag failed")
            
    def submitflag(self, flag):
        flag = b2a(flag)
        data = {"flag": f"{flag}", "token": f"{self.token}"}
        try:
            # Content-Type: application/x-www-form-urlencoded
            # r = requests.post(url=self.url, headers=self.header, data=data, timeout=self.timeout)

            # Content-Type: application/json
            r = requests.post(url=self.url, headers=self.header, json=data, timeout=self.timeout)

            logging.info("Submit flag success")
            # print(r.text)

        except:
            logging.error("Exception occurred while submitting the flag")

    def run_round_attack(self):
        for i in range(self.round_num):
            ttime = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
            banner = "\n[ {} ] ---> Round attack {}\n".format(ttime, i+1)
            logflag_into_file(FLAG_FILE, banner)
            pinfo(banner)
            self.submitflags()
            sleep(self.round_time)


if __name__ == "__main__":
    AWD(submit_url, token, round_num=round_num, round_time=round_time).run_round_attack()
    
