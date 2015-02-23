__author__ = 'yuriybodnar'

import logging


def get_ambari_url(instance):
    return "".join(["http://", instance.public_dns_name, ":8080"])


def report(instance, config):
    logging.info("Instance ID: %s" % instance.id)
    logging.info("Instance public DNS: %s" % instance.public_dns_name)
    logging.info("To connect via SSH: ssh%s" % "@".join([config.aws_ami_default_user, instance.public_dns_name]))
    logging.info("Ambari: %s" % get_ambari_url(instance))