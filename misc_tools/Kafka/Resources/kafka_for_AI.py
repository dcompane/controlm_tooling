python -u << EOF

"""
(c) 2020 - 2024 Daniel Companeetz, BMC Software, Inc.
All rights reserved.

BSD 3-Clause License

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# SPDX-License-Identifier: BSD-3-Clause
For information on SDPX, https://spdx.org/licenses/BSD-3-Clause.html


Change Log
Date (YMD)    Name                  What
--------      ------------------    ------------------------
20240626      Daniel Companeetz     Initial work
20240703      Daniel Companeetz     Added -u to python to flush buffer when no tty

"""

from datetime import datetime
from time import sleep
from os import path

def basic_consume_loop(consumer, topics):
    # Some variables to start
    duration = {{job_duration}} * 60  # seconds

    # max duration is 23:59
    if duration == 0:
        job_duration = (23 * 60 + 59) * 60 # 23:59 hours in seconds.
    else:
        job_duration = duration

    print(f'Job Duration is set to {job_duration}')

    # Set start time
    now = datetime.now().time()   
    start_time = (now.hour * 60 + now.minute) * 60 + now.second

    msg_number = 0
    running = True

    try:
        # Subscribe to the topic
        consumer.subscribe(topics)

        # loop on the messages
        while running:
            # if there are no messages timeout is 1 second
            # consumer.poll reads just one message!
            msg = consumer.poll(timeout=1.0)
            # if no messages
            if msg is None: 
                if get_out_time(start_time,job_duration): 
                    # comment next shutdown line to read again (endless loop?)
                    #   or leave uncommented to exit the loop and the program
                    print (f'No messages available in topic {topics} . Time limit exceeded. Exiting. rc=0')
                    running = shutdown()
                else:
                    # Wait a bit to see if there are new messages before exiting
                    sleep(5)

                continue

            # If there are errors
            if msg.error():
                # End of Partition message is ok. Just record it and continue
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    # Unexpected error occured
                    raise KafkaException(msg.error())
            else:  #NO ERRORS!!
                # there is at least one message
                msg_number += 1
                msg_process(msg_number,msg)

            if get_out_time(start_time, job_duration):
                print ("Max job duration reached. Exiting. rc=0")
                running=shutdown()

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

    return

def shutdown():
    # if loop needs to exit, set to false
    shut = False
    return shut

def get_out_time(start_time, job_duration): 
    now = datetime.now().time()
    now_time = (now.hour*60+now.minute)*60+now.second
    get_out = False
    if now_time > start_time + job_duration:
        get_out = True
    
    return get_out

def msg_process(number,message):
    # Write the message to a file
    # The message is a consumer object
    message = message.value().decode('UTF-8')
    directory = r'{{file_path}}'
    file_name = path.join(directory, f'{{file_name_prefix}}_{{file_name_body}}_{number}.{{file_extension}}')
    with open(file_name, 'w') as file:
        file.write(message)
        print(f'Message number {number} was written to {file_name}')
    file.close()

    return
    
from confluent_kafka import Consumer
# from  consumer_cloud import conf
# from consumer_platform import conf
conf = {'bootstrap.servers': '{{bootstrap_server}}:{{bootstrap_port}}',
        'group.id': '{{group_id}}',
        'auto.offset.reset': 'smallest'
        }

if __name__ == "__main__":
    #Initialize the consumer object
    consumer = Consumer(conf)

    #define the topics list
    topics = ["{{topic}}"]

    # invoke the consumer loop[]
    basic_consume_loop(consumer, topics)

EOF