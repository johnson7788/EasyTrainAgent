#启动1个sshd的服务，方便连接容器进行调试
mkdir /root/.ssh
cp authorized_keys /root/.ssh
chmod 600 /root/.ssh/authorized_keys
mkdir -p /run/sshd
chmod 755 /run/sshd
echo "配置了authorized_keys，并开启sshd服务，可以使用连接服务器ssh -p 7521 root@idc"
/usr/sbin/sshd -p 7521 -D