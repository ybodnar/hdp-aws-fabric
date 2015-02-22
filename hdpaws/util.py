__author__ = 'yuriybodnar'

def get_ambari_url(instance):
    return "".join(["http://", instance.public_dns_name, ":8080"])


def report(instance):
    print "Instance ID:", instance.id
    print "Instance public DNS", instance.public_dns_name
    print "To connect via SSH:  ", "ssh", "@".join([config.aws_ami_default_user, instance.public_dns_name])
    print "Ambari:  ", get_ambari_url(instance)