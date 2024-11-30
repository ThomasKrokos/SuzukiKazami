import Pyro5.api
import Pyro5.server
# RUN THIS FILE AFTER nameserver.py

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode="single")
class Process(object):
    def __init__(self, pid):
        print(f"created process{pid}")
        self.pid = pid  # Process ID
        self.request_queue = []  # Queue of requests in waiting to get the token
        self.has_token = False  # Indicator of critical section access
        self.seq_num = 0
        self.token_manager = TokenManager(5)


        
    def request_critical_section(self):
        req = {"seq_num" : self.seq_num, "pid": self.pid}
        self.request_queue.append(req)
        self.request_queue.sort(key=lambda x: (x['seq_num'], x['pid']))
        self.token_manager.request(req)
        if self.seq_num == 0:
            self.receive_token(-1)
        self.seq_num += 1

    def release_critical_section(self):
        if self.has_token and len(self.request_queue) > 0:
            print(f"process{self.pid} releasing from the critical section and passing token to process{self.request_queue[0]["pid"]}\n")
            self.token_manager.send_token({"old_pid": self.pid, "new_pid": self.request_queue[0]["pid"]})
            self.has_token = False
        elif len(self.request_queue) == 0:
            print(f"process{self.pid} has no one to pass the token to and is thus relinquishing it")
            self.has_token = False
        else:
            print(f"process{self.pid} does not have the token unable to pass token onwards\n")

    def receive_request(self, req):
            print(f"process{req['pid']}'s request received by process{self.pid}\n")
            self.seq_num = max(self.seq_num, req['seq_num'])+1
            self.request_queue.append(req)
            self.request_queue.sort(key=lambda x: (x['seq_num'], x['pid']))

    def receive_token(self, former_pid):
        if former_pid == -1:
            print(f'process{self.pid} is the first to access the critical section and has received the token')
            self.has_token = True
            self.request_queue = self.clear_req_queue(self.request_queue, self.pid)
        else: 
            print(f"process{self.pid} is next in line for the critical section and just received token from {former_pid}.\n")
            self.has_token = True
            self.request_queue = self.clear_req_queue(self.request_queue, self.pid)
        
    def clear_req_queue(self, queue, pid):
        queue.sort(key=lambda x: (x['seq_num'], x['pid']))
        for i in range(len(queue)):
            if queue[i]["pid"] == pid:
                del queue[:i+1]
                return queue  
        return queue

    def set_token_manager(self, token_manager):
        self._token_manager = token_manager
        
    def get_pid(self):
        return self.pid
    
    def has_critical_access(self):
        return self.has_critical_access

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode="single")
class TokenManager(object): 
    def __init__(self, process_num):
        self.process_num = process_num
    
    def request(self, req):
        print(f"Broadcasting process{req['pid']}'s request for the critical section to rest of processes, sequence number of request is {req['seq_num']}.\n")
        for i in range(self.process_num):
            if i != req['pid']:
                process_uri = f"PYRONAME:process.{i}"
                process = Pyro5.api.Proxy(process_uri)
                process.receive_request(req)         

    def send_token(self, req):
        process_uri = f"PYRONAME:process.{req['new_pid']}"
        process = Pyro5.api.Proxy(process_uri)
        process.receive_token(req['new_pid'])     

@Pyro5.server.expose
class Process0(Process):
    def __init__(self):
        super().__init__(0)

@Pyro5.server.expose
class Process1(Process):
    def __init__(self):
        super().__init__(1)

@Pyro5.server.expose
class Process2(Process):
    def __init__(self):
        super().__init__(2)

@Pyro5.server.expose
class Process3(Process):
    def __init__(self):
        super().__init__(3)

@Pyro5.server.expose
class Process4(Process):
    def __init__(self):
        super().__init__(4)


if __name__ == "__main__":
    
    print("please run nameserver.py first")
    token_manager = TokenManager(5)

    print("Registering processes and token manager with pyro...")
    daemon = Pyro5.server.Daemon()         
    ns = Pyro5.api.locate_ns()             
    uri = daemon.register(TokenManager)   # register the process as a Pyro object
    ns.register(f"tokenmanager", uri) 
    print(f"registered tokenmanager")
    
    urip0 = daemon.register(Process0)   # register the process as a Pyro object
    ns.register(f"process.0", urip0) 
    print(f"registered process0")

    urip1 = daemon.register(Process1)   # register the process as a Pyro object
    ns.register(f"process.1", urip1) 
    print(f"registered process1")
    
    urip2 = daemon.register(Process2)   # register the process as a Pyro object
    ns.register(f"process.2", urip2) 
    print(f"registered process2")
        
    urip3 = daemon.register(Process3)   # register the process as a Pyro object
    ns.register(f"process.3", urip3) 
    print(f"registered process3")
        
    urip4 = daemon.register(Process4)   # register the process as a Pyro object
    ns.register(f"process.4", urip4) 
    print(f"registered process4")
    
    print("Server is ready.")
    daemon.requestLoop()
    
    