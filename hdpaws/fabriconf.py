import random
import string
import time

__author__ = 'yuriybodnar'

from fabric.api import *
from fabric.contrib.files import sed, append

class FabricConfigurator:

    def __init__(self, ec2Instance, config):
        env.hosts = [ec2Instance.public_dns_name]
        env.host_string = ec2Instance.public_dns_name

        env.user = config.aws_ami_default_user
        env.key_filename = config.ssh_key

        time.sleep(config.initialization_timeout_seconds)

        self.ambari_repo_url=config.ambari_repo_url
        self.ec2Instance = ec2Instance

    def install_ambari(self):
        run("wget -nv {url}".format(url=self.ambari_repo_url))
        sudo("mv ambari.repo /etc/yum.repos.d/")
        sudo("yum install -y ambari-server")

    def setup_ambari(self):
        sudo("ambari-server setup --silent")

    def configure_networking(self):
        run("sudo chkconfig iptables off")
        hostname = run("hostname -A")
        privateIp = run("ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'")
        sed("/etc/sysconfig/network", before="localhost.localdomain", after=hostname, use_sudo=True)
        append("/etc/hosts", "{ip}  {host}".format(host=hostname, ip=privateIp), use_sudo=True)
        sudo("service network restart")
        sudo("hostname {intIp}".format(intIp=self.ec2Instance.private_dns_name))

    def generate_root_password(self):
        return "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(20))

    def configure_root_account(self):
        password=self.generate_root_password()
        sudo("echo -e '{password}\n{password}' | passwd").format(password=password)
        run("sudo ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''")
        sudo("chown -R root:root /root/.ssh")
        # run("sudo cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys")

    def start_ambari(self):
        run("sudo /etc/init.d/ambari-server start")

    def install_ambari_agent(self, ambari_server_hostname):
        run("sudo yum install -y ambari-agent")
        sed("/etc/ambari-agent/conf/ambari-agent.ini",before="hostname=localhost"
            , after="hostname={hostname}".format(hostname=ambari_server_hostname)
            ,use_sudo=True)
        run("sudo /etc/init.d/ambari-agent start")
