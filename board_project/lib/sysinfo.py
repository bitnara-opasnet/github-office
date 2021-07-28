from numpy import broadcast
import psutil
import platform

def get_hw_idle_info(): 
    rst = dict() 

    # CPU 데이터
    cp = psutil.cpu_times_percent(interval=None, percpu=False) 
    cp_item = dict()
    cp_item['free'] = psutil.cpu_count(logical=False) * (cp.idle/100) # Physical
    cp_item['idle'] = cp.idle
    cp_item['desc'] = "Idle CPU: {} core ({:.1f})".format(cp_item['free'], cp_item['idle'])
    rst['cpu'] = cp_item

     # 메모리 데이터
    vm = psutil.virtual_memory()
    vm_item = dict()
    vm_item['free'] = vm.available//(1024*1024)
    vm_item['idle'] = vm.available/vm.total*100
    vm_item['desc'] = "Idle Memory: {}MB ({:.2f}%)".format(vm_item['free'], vm_item['idle'])
    rst['memory'] = vm_item

    # 디스크 데이터
    du = psutil.disk_usage(path='/') 
    du_item = dict()
    du_item['free'] = du.free//(1024*1024)
    du_item['idle'] = du.free/du.total*100
    du_item['desc'] = "Idle Disk: {}MB ({:.1f}%)".format(du_item['free'], du_item['idle'])
    rst['disk'] = du_item
    return rst

def getLoad():
    cpu_result, mem_result, swap_result, disk_result, network_result = {}, {}, {}, {}, {}
    # CPU
    cpu = psutil.cpu_times_percent()
    total = cpu.user + cpu.system + cpu.idle
    if total > 100:
        cpu_result['user'] = 100 - (cpu.system + cpu.idle)
    else:
        cpu_result['user'] = cpu.user
    if total < 100:
        cpu_result['idle'] = 100 - (cpu.system + cpu_result['user'])
    else:
        cpu_result['idle'] = cpu.idle
    cpu_result['count'] = psutil.cpu_count(logical=False)
    cpu_result['kernel'] = cpu.system
    cpu_result['idle'] = '{}%'.format(cpu.idle)
    cpu_result['freq'] = '{:.2f} GHz'.format(psutil.cpu_freq().current/1024)
    # mem
    mem = psutil.virtual_memory()
    # mem_result['total'] = mem.total/1024.    # kbytes
    # mem_result['used'] = mem.used/1024.
    # mem_result['free'] = mem.available/1024.
    mem_result['total'] = '{:.2f} MB'.format(mem.total/1024**2)
    mem_result['used'] = '{:.2f} MB'.format(mem.used/1024**2)
    mem_result['free'] = '{:.2f} MB'.format(mem.available/1024**2)
    # swap
    swap = psutil.swap_memory()
    # swap_result['total'] = swap.total/1024.    # kbytes
    # swap_result['used'] = swap.used/1024.
    # swap_result['free'] = swap.free/1024.
    swap_result['total'] = '{:.2f} MB'.format(swap.total/1024**2)
    swap_result['used'] = '{:.2f} MB'.format(swap.used/1024**2)
    swap_result['free'] = '{:.2f} MB'.format(swap.free/1024**2)
    # disk
    partitions = psutil.disk_partitions()
    for partition in partitions:
        diskInfo = psutil.disk_usage(partition.mountpoint)
        disk_result[partition.mountpoint] = {'used':'{} %' .format(diskInfo.percent), 'total': '{:.2f} GB'.format(diskInfo.total/1024**3)}
    #network
    networks = psutil.net_if_addrs()
    keys = list(networks.keys())
    net_list = []
    for key in keys:
        net_info = networks.get(key)
        imsi_list=[]
        for i in net_info:
            net_dict = {'address':i.address, 'netmask':i.netmask, 'broadcast':i.broadcast}
            imsi_list.append(net_dict)
        net_list.append({key:imsi_list})
    network_result = []
    for i in net_list:
        network_result.append(i)
    return {'cpu':cpu_result, 'memory': mem_result, 'swap': swap_result, 'disk': disk_result, 'network': network_result}

def getplatform():
    Kernel = platform.platform()
    uname = platform.uname()
    system = platform.system()
    node = platform.node()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()
    rst = {'Kernel':Kernel, 'uname':uname, 'system':system, 'node':node, 'release':release, 'version':version, 'machine':machine, 'processor':processor}
    return rst

def net_io():
    net = psutil.net_io_counters()
    sent = net.bytes_sent/1024**2
    recv = net.bytes_recv/1024**2
    return round(sent, 2), round(recv, 2)