import requests
import json, re
import os
from io import StringIO
from xml.etree import ElementTree

ONVIF_DEVICE_SERVICE_PATH = '/onvif/device_sevice'
ONVIF_GET_PROFILE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
xmlns:trt="http://www.onvif.org/ver10/media/wsdl">
<soap:Body>
<trt:GetProfiles/>
</soap:Body>
</soap:Envelope>"""

ONVIF_GET_SNAPSHOT_URI = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
xmlns:trt="http://www.onvif.org/ver10/media/wsdl"
xmlns:tt="http://www.onvif.org/ver10/schema">
<soap:Body>
<trt:GetSnapshotUri>
<trt:ProfileToken>{0}</trt:ProfileToken>
</trt:GetSnapshotUri>
</soap:Body>
</soap:Envelope>"""

ONVIF_GET_STREAM_URI = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
xmlns:trt="http://www.onvif.org/ver10/media/wsdl"
xmlns:tt="http://www.onvif.org/ver10/schema">
	<soap:Body>
		<trt:GetStreamUri>
			<trt:StreamSetup>
				<tt:Stream>RTP-Unicast</tt:Stream>
				<tt:Transport>
					<tt:Protocol>UDP</tt:Protocol>
				</tt:Transport>
			</trt:StreamSetup>
			<trt:ProfileToken>{0}</trt:ProfileToken>
		</trt:GetStreamUri>
	</soap:Body>
</soap:Envelope>"""

def parse_response(response):
    root = ElementTree.fromstring(response.text)

    namespaces = dict([
        node for _, node in ElementTree.iterparse(
            StringIO(response.text), events=['start-ns']
        )
    ])

    return root, namespaces

def get_device_profiles(ip_addr):
    headers = { 'Content-Type': 'application/xml' }
    response = requests.post('http://' + ip_addr + ONVIF_DEVICE_SERVICE_PATH, data=ONVIF_GET_PROFILE_XML, headers=headers)
    #print(response.text)

    # define namespace mappings to use as shorthand below
    #namespaces = {
    #    's': 'http://www.w3.org/2003/05/soap-envelope',
    #    'trt': 'http://www.onvif.org/ver10/media/wsdl',
    #    'tt': 'http://www.onvif.org/ver10/schema',
    #}

    root, namespaces = parse_response(response)

    profiles = root.findall(
        './s:Body'
        '/trt:GetProfilesResponse'
        '/trt:Profiles',
        namespaces
    );

    return [ret.get('token') for ret in profiles]


def get_snapshot_uri(ip_addr, token):
    get_snapshot_uri_xml = ONVIF_GET_SNAPSHOT_URI.format(token)

    headers = { 'Content-Type': 'application/xml' }
    response = requests.post('http://' + ip_addr + ONVIF_DEVICE_SERVICE_PATH, data=get_snapshot_uri_xml, headers=headers)

    root, namespaces = parse_response(response)

    snapshot_uri = root.find(
        './s:Body'
        '/trt:GetSnapshotUriResponse'
        '/trt:MediaUri'
        '/tt:Uri',
        namespaces
    );

    if snapshot_uri is not None:
    	return snapshot_uri.text

    return None

def get_stream_uri(ip_addr, token):
    get_stream_uri_xml = ONVIF_GET_STREAM_URI.format(token)

    headers = { 'Content-Type': 'application/xml' }
    response = requests.post('http://' + ip_addr + ONVIF_DEVICE_SERVICE_PATH, data=get_stream_uri_xml, headers=headers)

    root, namespaces = parse_response(response)

    stream_uri = root.find(
        './s:Body'
        '/trt:GetStreamUriResponse'
        '/trt:MediaUri'
        '/tt:Uri',
        namespaces
    );

    if stream_uri is not None:
    	return stream_uri.text

    return None


if __name__ == '__main__':
    ip_addr = '192.168.0.150'
    tokens = get_device_profiles(ip_addr)
    print(tokens)

    snapshot_uri = get_snapshot_uri(ip_addr, tokens[0])
    print(snapshot_uri)

    stream_uri = get_stream_uri(ip_addr, tokens[0])
    print(stream_uri)

    #with open('/opt/janus/etc/janus/janus.plugin.streaming.jcfg') as f:
    #    file_string = f.read()
    #    #print(file_string)
    #    file_trimmed = re.sub("#.*", "", file_string, flags=re.MULTILINE)
    #    print(file_trimmed)
    #    data = json.loads('{' + file_trimmed + '}')

    #print(data)

    print('Restarting WebRTC Server')
    os.system('sudo systemctl restart webrtcserver')
    print('Restarted OK')
