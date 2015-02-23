__author__ = 'yuriybodnar'

import random
import string
import time

from fabric.api import *
from fabric.contrib.files import sed, append


AMBARI_SERVER_INIT_SCRIPT = "/etc/init.d/ambari-server"
AMBARI_AGENT_CONFIG_FILE = "/etc/ambari-agent/conf/ambari-agent.ini"
AMBARI_AGENT_INIT_SCRIPT = "/etc/init.d/ambari-agent"
SUDOERS_FILE = "/etc/sudoers"


class FabricConfigurator:
    def __init__(self, ec2Instance, config):
        env.hosts = [ec2Instance.public_dns_name]
        env.host_string = ec2Instance.public_dns_name

        env.user = config.aws_ami_default_user
        env.key_filename = config.ssh_key

        time.sleep(config.initialization_timeout_seconds)

        self.ambari_repo_url = config.ambari_repo_url
        self.ec2Instance = ec2Instance

    def install_ambari_server(self):
        run("wget -nv {url}".format(url=self.ambari_repo_url))
        sudo("mv ambari.repo /etc/yum.repos.d/")
        sudo("yum install -y ambari-server")

    def setup_ambari_server(self):
        sudo("ambari-server setup --silent")

    def configure_networking(self):
        run("sudo chkconfig iptables off")
        hostname = run("hostname -A")
        privateIp = run("ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'")
        sed("/etc/sysconfig/network", before="localhost.localdomain", after=hostname, use_sudo=True)
        append("/etc/hosts", "{ip}  {host}".format(host=hostname, ip=privateIp), use_sudo=True)
        sudo("service network restart")
        sudo("hostname {intIp}".format(intIp=self.ec2Instance.private_dns_name))
        self.allow_sudo_without_tty()

    def generate_root_password(self):
        return "".join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(20))

    def configure_root_account(self):
        password = self.generate_root_password()
        sudo("echo -e '{password}\n{password}' | passwd").format(password=password)
        run("sudo ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''")
        sudo("chown -R root:root /root/.ssh")
        # run("sudo cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys")

    def start_ambari_server(self):
        time.sleep(15)
        sudo("{ambari_server} start".format(ambari_server=AMBARI_SERVER_INIT_SCRIPT), pty=False)


    def install_ambari_agent(self):
        run("sudo yum install -y ambari-agent")


    def setup_ambari_agent(self, ambari_server_hostname):
        sed(AMBARI_AGENT_CONFIG_FILE, before="hostname=localhost"
            , after="hostname={hostname}".format(hostname=ambari_server_hostname)
            , use_sudo=True)

    def start_ambari_agent(self):
        time.sleep(15)
        sudo("{ambari_agent} start".format(ambari_agent=AMBARI_AGENT_INIT_SCRIPT), pty=False)

    def allow_sudo_without_tty(self):
        sed(SUDOERS_FILE, before="Defaults    requiretty", after="#Defaults    requiretty", use_sudo=True)

