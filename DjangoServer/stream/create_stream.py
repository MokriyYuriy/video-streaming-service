import hashlib
import requests
from random import randint
from .models import RTSPServer

def create_stream(stream_id):
    for i in range(10):
        random_stream_addr = (RTSPServer.objects.all()[randint(0, RTSPServer.objects.count() - 1)]).address
        stream_name = 'stream_' + str(stream_id)
        in_stream = 'rtmp://' + random_stream_addr + '/src/' + stream_name
        out_stream = 'http://' + random_stream_addr + '/live/' +  stream_name + '.m3u8'
        key = hashlib.sha224(bytes(in_stream + 'SECRET' + out_stream, 'utf-8')).hexdigest()
        in_stream += '?key=' + key
        print('http://' + random_stream_addr + '/add_stream')
        r = requests.post('http://' + random_stream_addr + '/add_stream',
                          data = {'name' : stream_name, 'key' : key})
        if r.status_code // 100 == 2:
            return in_stream, out_stream
    return 'None', 'None' 
    
