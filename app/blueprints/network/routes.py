from flask import Blueprint, jsonify
import subprocess
import platform
import socket
import threading
import ipaddress
import ping3
from datetime import datetime

network_bp = Blueprint('network', __name__)

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def scan_network(ip_range):
    """Scan network for active devices"""
    devices = []
    network = ipaddress.ip_network(ip_range, strict=False)
    
    def ping_host(ip):
        try:
            response_time = ping3.ping(str(ip), timeout=1)
            if response_time is not None:
                try:
                    hostname = socket.gethostbyaddr(str(ip))[0]
                except:
                    hostname = ''
                
                return {
                    'ip': str(ip),
                    'hostname': hostname,
                    'status': 'online',
                    'response_time': round(response_time * 1000, 2)
                }
        except:
            pass
        return None
    
    threads = []
    results = []
    
    for ip in network.hosts():
        thread = threading.Thread(target=lambda: results.append(ping_host(ip)))
        thread.start()
        threads.append(thread)
        
        # Limit concurrent threads
        if len(threads) >= 100:
            for t in threads:
                t.join()
            threads = []
    
    for t in threads:
        t.join()
    
    devices = [r for r in results if r is not None]
    return devices

@network_bp.route('/status', methods=['GET'])
def get_network_status():
    """Get network status information"""
    try:
        local_ip = get_local_ip()
        network = ipaddress.ip_network(f'{local_ip}/24', strict=False)
        
        # Get gateway
        gateway = str(list(network.hosts())[0])
        
        # Scan for devices
        devices = scan_network(str(network))
        
        return jsonify({
            'local_ip': local_ip,
            'gateway': gateway,
            'subnet': str(network),
            'total_devices': len(devices),
            'devices': devices,
            'last_scan': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_bp.route('/ping/<host>', methods=['GET'])
def ping_host(host):
    """Ping a specific host"""
    try:
        response_time = ping3.ping(host, timeout=2)
        if response_time is not None:
            return jsonify({
                'host': host,
                'status': 'online',
                'response_time': round(response_time * 1000, 2)
            })
        else:
            return jsonify({
                'host': host,
                'status': 'offline',
                'response_time': None
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500