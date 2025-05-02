apt install ethtool


ethtool -s eno2 wol g

iptables -I INPUT -p udp --dport 9 -j ACCEPT
iptables -I INPUT -p udp --dport 7 -j ACCEPT

netfilter-persistent save
