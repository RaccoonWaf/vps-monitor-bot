PROTOCOLS = {
    "openvpn": {
        "name": "OpenVPN",
        "ports": [1194, 443, 8443, 943],
    },
    "wireguard": {
        "name": "WireGuard",
        "ports": [51820, 51821, 443, 45137],
    },
    "shadowsocks": {
        "name": "Shadowsocks / Outline",
        "ports": [8388, 8389, 443, 80],
    },
    "xray": {
        "name": "Xray / VLESS / VMess",
        "ports": [443, 8443, 80, 8080, 9443],
    },
    "other": {
        "name": "Другое",
        "ports": [443, 80, 22, 8443, 8080],
    },
}

ALLOWED_PORTS = sorted({
    port
    for data in PROTOCOLS.values()
    for port in data["ports"]
})
