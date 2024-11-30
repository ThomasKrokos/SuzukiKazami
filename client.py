from Pyro5.api import Proxy

# RUN THIS FILE AFTER server.py

if __name__ == "__main__":
    print("Pulling objects from pyro server \n")
    process0 = Proxy("PYRONAME:process.0")
    print(process0)
    process1 = Proxy("PYRONAME:process.1")
    print(process1)
    process2 = Proxy("PYRONAME:process.2")
    print(process2)
    process3 = Proxy("PYRONAME:process.3")
    print(process3)
    process4 = Proxy("PYRONAME:process.4")
    print(process4)
    token_manager = Proxy("PYRONAME:tokenmanager")
    print(token_manager)

    try:
        print("testing token algorithm ...")
        process0.set_token_manager(token_manager)
        process1.set_token_manager(token_manager)
        process2.set_token_manager(token_manager)
        process3.set_token_manager(token_manager)
        process4.set_token_manager(token_manager)
        
        process0.request_critical_section()
        process1.request_critical_section() 
        process2.request_critical_section() 
        
        process0.release_critical_section() # manually release critical section
        
        process3.request_critical_section()
        process4.request_critical_section()
        
        process0.request_critical_section() 
        
        process0.release_critical_section() # should fail since process 0 does not have token yet
        
        process1.release_critical_section() # manually release critical section
        process2.release_critical_section() # manually release critical section
        process3.release_critical_section() # manually release critical section
        process4.release_critical_section() # manually release critical section
        
        process0.release_critical_section() # manually release critical section
        
        # release one more time to check that no process is in the critical section
        process0.release_critical_section() # manually release critical section
        process1.release_critical_section() # manually release critical section
        process2.release_critical_section() # manually release critical section
        process3.release_critical_section() # manually release critical section
        process4.release_critical_section() # manually release critical section
        print("ending tests of Suzuki Kazami algorithm")
        
        
    except Exception as e:
        print(f"error: {e}")
    