***
### Enable note service (awake remote if files changed local)

```shell
    sudo setcap cap_net_raw,cap_net_admin+ep $(which arping)
```


```shell

    cat > /etc/systemd/system/wake_lzwork__on_fmod.service << EOF
    [Unit]
    Description=Run wrapper__wake_lzwork when changes in trend
    # (если скрипту нужен сеть/БД — раскомментируйте)
    After=network-online.target
    Wants=network-online.target
    
    [Service]
    Type=oneshot
    WorkingDirectory=/home/zhenka/junk/trend/modules/PlayerLiteRun/
    ExecStart=/home/zhenka/bin/wrapper__wake_lzwork
    EOF

    # vim /etc/systemd/system/wake_lzwork__on_fmod.service 
    systemctl daemon-reload
    systemctl enable --now wake_lzwork__on_fmod.service
```

```shell
    cat > /etc/systemd/system/wake_lzwork__on_fmod.timer << EOF
    [Unit]
    Description=Every minute run wake_lzwork__on_fmod.service
    
    [Timer]
    OnBootSec=10           
    OnUnitActiveSec=60    
    AccuracySec=10         
    Persistent=true         
    
    [Install]
    WantedBy=timers.target
    EOF

    # vim /etc/systemd/system/wake_lzwork__on_fmod.timer 
    systemctl daemon-reload
    systemctl enable --now wake_lzwork__on_fmod.timer

```
