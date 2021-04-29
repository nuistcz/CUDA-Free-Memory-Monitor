from pynvml import *
import argparse
import requests
import time
import sys

class GPUStat:
    def __init__(self, api, t, m):
        nvmlInit()
        self.deviceCount = nvmlDeviceGetCount()
        self.var = 1
        self.api = api
        self.t = t
        self.m = m * 100
        super()

    def test(self):
        print(self.var)

    def lookMem(self, id, out=False):
        handle = nvmlDeviceGetHandleByIndex(id)
        info = nvmlDeviceGetMemoryInfo(handle)
        gpuname =  nvmlDeviceGetName(handle)
        tmp = nvmlDeviceGetTemperature(handle, 0)
        mem = info.free / 1024**2
        freemem = '{:.2f}'.format(info.free/info.total*100)
        if out:
            # print('GPU Index:', id, 'GPU Name:', gpuname,
            #       'Free Memory:', mem, 'Mem left(%):', freemem)
            print('GPU Index:{}, GPU:{}, Free Memory:{}M,\tMem left: {}%'.format(id, gpuname, mem, freemem))
            return id, gpuname, mem, freemem
        else:
            return id, gpuname, mem, freemem

    def monitor(self):
        print('Attempt to get GPUstat')
        for i in range(self.deviceCount):
            id, gpuname, mem, freemem = self.lookMem(i, out=True)
            if float(freemem) > self.m:
                self.server_post(id, gpuname, mem, freemem)

    def server_post(self, id, gpuname, mem, freemem):
        print('Find Usable GPU! Sending Message...')
        api = self.api
        title = 'Find Space GPU'
        content = 'GPU Index:{}, GPU:{}, Free Memory:{}M,\tMem left: {}%'.format(id, gpuname, mem, freemem)
        data = {
            "text": title,
            "desp": content
        }
        req = requests.post(api, data=data)
        print('Send Message Done, %s' % req.text)
        print('Program Reactivate after 1 hour!')
        time.sleep(self.t)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', '-a', require=True, type=str, help='ServerApi For Post')
    parser.add_argument('--time', '-t', default=3600, type=int, help='Cooling time after posting')
    parser.add_argument('--mem', '-m', default=0.9, type=float, help='Threshold Memory for Alarming')
    args = parser.parse_args(params)
    
    gpu = GPUStat(args.api, args.time, args.mem)
    while (1):
        gpu.monitor()
        time.sleep(10)

