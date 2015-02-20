__author__ = 'yuriybodnar'

import time
import random
import string
import boto.ec2
from fabric.api import *
from fabric.contrib.files import sed, append

import config

params = {"image_id": config.aws_ami,
          "key_name": config.aws_key_name,
          "instance_type": config.ec2_instance_type,
          "security_group_ids": [ config.ec2_security_group_id ],
          "subnet_id": config.ec2_subnet_id}

def get_connection():
    return boto.ec2.connect_to_region(config.aws_region_name)

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
    run("wget -nv {url}".format(url=config.ambari_repo_url))
    sudo("mv ambari.repo /etc/yum.repos.d/")
    sudo("yum install -y ambari-server")

def setup_ambari():
    sudo("ambari-server setup --silent")

def configure_networking(instance_):
    run("sudo chkconfig iptables off")
    hostname = run("hostname -A")
    privateIp = run("ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'")
    sed("/etc/sysconfig/network", before="localhost.localdomain", after=hostname, use_sudo=True)
    append("/etc/hosts", "{ip}  {host}".format(host=hostname, ip=privateIp), use_sudo=True)
    sudo("service network restart")
    sudo("hostname {intIp}".format(intIp=instance_.private_dns_name))

def generate_root_password():
    return "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(20))

def configure_root_account():
    password=generate_root_password()
    sudo("echo -e '{password}\n{password}' | passwd").format(password=password)
    run("sudo ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''")
    sudo("chown -R root:root /root/.ssh")


def start_ambari():
    sudo("service ambari-server start")


if __name__ == "__main__":
    connection = get_connection()
    reservation = connection.run_instances(**params)
    instance_id = get_instance_id(reservation)

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

    env.user = config.aws_ami_default_user
    env.key_filename = config.ssh_key
    time.sleep(config.initialization_timeout_seconds)

    configure_networking(instance)
    configure_root_account()

    install_ambari()
    setup_ambari()
    start_ambari()

    print "Instance ID:", instance_id
    print "Instance public DNS", instance.public_dns_name
    print "To connect via SSH:  ", "ssh", "@".join([config.aws_ami_default_user, instance.public_dns_name])
    print "Ambari:  ", "".join(["http://", instance.public_dns_name, ":8080"])