__author__ = 'yuriybodnar'

import boto.ec2
from fabric.api import *
from fabric.contrib.files import sed, append
import time

#AMI = "ami-146e2a7c" #Amazon Linux
AMI = "ami-02dc4c6b"
params = {"image_id": AMI,
          "key_name": "aws_rsa",
          "instance_type": "m3.medium",
          "security_group_ids": ["~"],
          "subnet_id": "~"}
SSH_USER = "ec2-user"
SSH_KEY = "~/.ssh/aws_rsa"

def get_connection():
    return boto.ec2.connect_to_region("us-east-1")

def get_instance_id(reservation_):

    myInstanceId = reservation.instances[0].id
    if not myInstanceId:
        raise Exception("Did not get instance Id")
    return myInstanceId

def get_instance(connection_,instance_id_):
    result = None
    for instance in connection_.get_all_reservations(instance_ids=[instance_id_])[0].instances:
        if instance.id in instance_id_:
            result = instance
            break
    if not result:
        raise Exception("Could not find instance")
    return result

def install_ambari():
    run("wget -nv http://public-repo-1.hortonworks.com/ambari/centos6/1.x/updates/1.7.0/ambari.repo")
    run("sudo mv ambari.repo /etc/yum.repos.d/")
    sudo("sudo yum install -y ambari-server")

def setup_ambari():
    sudo("ambari-server setup --silent")


def configure_networking():
    run("sudo chkconfig iptables off")
    hostname = run("hostname -A")
    privateIp = run("ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'")
    sed("/etc/sysconfig/network", before="localhost.localdomain", after=hostname, use_sudo=True)
    append("/etc/hosts", "{ip}  {host}".format(host=hostname, ip=privateIp), use_sudo=True)
    sudo("service network restart")

def configure_root_account():
    sudo("echo -e 'SDLAKJD@@1123eeaa\nSDLAKJD@@1123eeaa' | passwd")
    run("sudo ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''")
    sudo("chown -R root:root /root/.ssh")


if __name__ == "__main__":
    connection = get_connection()
    reservation = connection.run_instances(**params)
    instance_id = get_instance_id(reservation)
    # instance_id = "i-41c043ae"
    print "Instance ID:", instance_id
    time.sleep(10)

    instance = get_instance(connection, instance_id)
    while instance.state not in "running":
        print 'Waiting for instance to init'
        print "Instance state:", instance.state
        time.sleep(5)
        instance = get_instance(connection, instance_id)

    print "Instance state:", instance.state
    print "Instance Public DNS:", instance.public_dns_name

    env.hosts = [instance.public_dns_name]
    env.host_string = instance.public_dns_name

    env.user = SSH_USER
    env.key_filename = SSH_KEY
    time.sleep(60)

    configure_networking()
    configure_root_account()

    install_ambari()
    setup_ambari()
