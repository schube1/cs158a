import socket
import uuid
import threading
import time
import json

## each node operates as a client and server
## send your UID to the next node and recieve one aswell. You only ever forward a message if its larger than ur value.
## Node knows its the leader once it gets back its own ID -> it was larger than all in the circle


# each new node needs to get this
with open("config.txt", 'r') as config:
        # read in lines of config , strip \n and split using ',' and set ports to int()
    lines = config.readlines()
    server_ip, server_port = lines[0].strip().split(",")
    client_ip, client_port = lines[1].strip().split(",")
    server_port = int(server_port)
    client_port = int(client_port)

# initalize current id, state, leader ID
node_uuid = uuid.uuid4()
state = 0
leader_id = None
connection_in = None

with open("log.txt", 'w') as logfile:
    logfile.write(f"UUID: {node_uuid}\n")

def write_log(txt):
    with open("log.txt",'a') as log:
        log.write(txt + "\n")



class Message:  
    def __init__(self, uuid, flag):
        # for flag 0: still in the process of leader election (initial value).. 1: leader is already elected
        self.uuid = uuid            
        self.flag = flag

def server_setup():
    global connection_in
    # AF_INET  = IPv4 address family
    # SOCK_STREAM = TCP (reliable, connection-oriented)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:

        # Allow reusing the port immediately after the server stops.
        # Without this, you'd get "Address already in use" for ~60 seconds.
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket host & port
        server_sock.bind((server_ip, server_port))
        
        #waiting for client
        server_sock.listen(1)
        print(f"Listening on {server_ip}:{server_port}")

        #accpet one connection
        conn, addr = server_sock.accept()
        # now that we have the connection established and no other connections will occur to this socket it can be closed
        connection_in = conn
    
def client_setup():
    #create a TCP socket 
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the next node
    client_sock.connect((client_ip, client_port))

    return client_sock

#start the server setup in new thread so that accept doesnt cause deadlock
server_thread = threading.Thread(target=server_setup)
server_thread.start()

#reasonable length of sleep time to wait for a server node to be up
time.sleep(5)

#connect this node client side to the next node
client_sock = client_setup()
server_thread.join()


message = Message(node_uuid, 0)

# serialize the message instance to json
msg_json = json.dumps({
    "uuid": str(message.uuid),
    "flag": message.flag
})

#you should send a message with your uuid (without any comparison) as the initial message
client_sock.sendall(msg_json.encode())
#need to log this aswell
write_log(f"Sent: uuid={message.uuid}, flag={message.flag}")

def receiving_message():
    buffer = ""
    #while theres no } we continue
    while True:
        d = connection_in.recv(256)
        buffer += d.decode()
        if "}" in buffer:
            break
    # load json to dict
    msg_data = json.loads(buffer)
    re_id = uuid.UUID(msg_data["uuid"])
    re_flag = msg_data["flag"]

    return Message(re_id, re_flag) #return the recieved uuid and flag


def handle_message(msg):
    global state
    global leader_id

    # we dont have a leader yet so election is in progress
    if msg.flag == 0:
        if msg.uuid  > node_uuid:
            #log the recieved
            write_log(f"Received: uuid={msg.uuid}, flag={msg.flag}, greater, 0")

            #need to forward
            forward_message = json.dumps({
                "uuid": str(msg.uuid),
                "flag": msg.flag
            })

            client_sock.sendall(forward_message.encode())
            #after the sendall call need to log the send
            write_log(f"Sent: uuid={msg.uuid}, flag={msg.flag}")
            return False
        
        elif msg.uuid < node_uuid:
            # ignore incoming message
            write_log(f"Received: uuid={msg.uuid}, flag={msg.flag}, less, 0")
            #assignment said to show the the msg was ignored
            write_log(f"Ignored: uuid={msg.uuid}, flag={msg.flag}")
            return False
        else:
            write_log(f"Received: uuid={msg.uuid}, flag={msg.flag}, same, 0") #state of incoming is still 0
            # this node is the leader
            state = 1
            leader_id = node_uuid
            #since i am leader I will announce it
            write_log(f"Leader is decided to {leader_id}")

            msg_leader_found = Message(node_uuid, 1) # message instance for when leader is identified


            json_msg_leader = json.dumps({
                "uuid": str(msg_leader_found.uuid),
                "flag": msg_leader_found.flag
            })
            client_sock.sendall(json_msg_leader.encode())
            write_log(f"Sent: uuid={msg_leader_found.uuid}, flag={msg_leader_found.flag}")
            
            return False
    # the leader has been elected as of now.
    elif msg.flag == 1:

        # log the recieved either greater less or same
        if msg.uuid > node_uuid:
            write_log(f"Received: uuid={msg.uuid}, flag={msg.flag}, greater, {state}")

        elif msg.uuid < node_uuid:
            write_log(f"Received: uuid={msg.uuid}, flag={msg.flag}, less, {state}")

        else:
            write_log(f"Received: uuid={msg.uuid}, flag={msg.flag}, same, {state}, leader_id={leader_id}")
            #leader is found 
        state = 1
        leader_id = msg.uuid


        #if not this node is not the leader forward else dont forward
        if msg.uuid != node_uuid:
            forward_message = json.dumps({
                "uuid": str(msg.uuid),
                "flag": msg.flag
            })
            client_sock.sendall(forward_message.encode())
            write_log(f"Sent: uuid={msg.uuid}, flag={msg.flag}")
            return True


        else: #this node is the leader
            #everyone else has heard that I am the leader
            return True
        
while True:
    received_msg = receiving_message()
    done = handle_message(received_msg)
    if done:
        break

print(f"leader is {leader_id}")







