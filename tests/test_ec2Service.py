__author__ = 'yuriybodnar'

from unittest import TestCase

from hdpaws.hdpaws.ec2service import *
import configyb


class TestEc2Service(TestCase):
    def test_provision(self):
        service = Ec2Service(configyb)

        testParams = {"image_id": configyb.aws_ami,
          "key_name": configyb.aws_key_name,
          "instance_type": configyb.ec2_instance_type,
          "security_group_ids": [ configyb.ec2_security_group_id ],
          "subnet_id": configyb.ec2_subnet_id}

        instance = service.provision_instance(testParams)
        print "Done"
