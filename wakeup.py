#!/usr/bin/env python3
"""
Send Wake-on-LAN magic packet.

usage:
    python wake_workstation.py 00:11:22:33:44:55
"""
import argparse
from wakeonlan import send_magic_packet      # pip install wakeonlan


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('mac', help='MAC-address of the workstation')
    p.add_argument('-b', '--broadcast', default='255.255.255.255',
                   help='broadcast IP (default 255.255.255.255)')
    p.add_argument('-p', '--port', type=int, default=9,
                   help='destination UDP port (default 9)')
    args = p.parse_args()
    send_magic_packet(args.mac,
                      ip_address=args.broadcast,
                      port=args.port)


if __name__ == '__main__':
    main()

