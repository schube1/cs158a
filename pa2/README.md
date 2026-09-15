## Set up for local demo

For the local demo, make three identical copies of myleprocess.py. I created sub directories for testing so I had node1/ , node2/ , node3/ each with their own copy of myleprocess.py and a config.txt.

### node1/config.txt:

    127.0.0.1,5001
    127.0.0.1,5002

### node2/config.txt:

    127.0.0.1,5002
    127.0.0.1,5003

### node3/config.txt:

    127.0.0.1,5003
    127.0.0.1,5001

This will allow us to create a ring of the three processes.

## Running the processes

To run each process, open three terminals side by side, then navigate to the corresponding node directory.
within those directories run this same command `python3 myleprocess.py`

## Terminal results 

### node1
    (base) vinzentschubert@Mac node1 % python3 myleprocess.py
    Listening on 127.0.0.1:5001
    leader is c8974085-6fe8-4d14-b19f-b714ae8e61af

### node2
    (base) vinzentschubert@Mac node2 % python3 myleprocess.py
    Listening on 127.0.0.1:5002
    leader is c8974085-6fe8-4d14-b19f-b714ae8e61af

### node3
    (base) vinzentschubert@Mac node3 % python3 myleprocess.py
    Listening on 127.0.0.1:5003
    leader is c8974085-6fe8-4d14-b19f-b714ae8e61af

#### See pa2/log1.txt , pa2/log2.txt , pa2/log3.txt to look at the logged outputs from this local demo.