__author__ = 'yuriybodnar'

import boto.ec2
import time
import logging


class Ec2Service:
    def __init__(self, config):
        self.config = config
        pass

    def get_connection(self):
        return boto.ec2.connect_to_region(self.config.aws_region_name)

    def get_instance_id(self, reservation_):
        myInstanceId = reservation_.instances[0].id
        if not myInstanceId:
            raise Exception("Did not get instance Id")
        return myInstanceId

    def get_instance(self, connection_, instance_id_):
        result = None
        for instance in connection_.get_all_reservations(instance_ids=[instance_id_])[0].instances:
            if instance.id in instance_id_:
                result = instance
                break
        if not result:
            raise Exception("Could not find instance")
        return result

    def provision_instance(self, params):
        self.connection = self.get_connection()
        reservation = self.connection.run_instances(**params)

        instance_id = self.get_instance_id(reservation)

        logging.info("Instance ID: %s" % instance_id)
        time.sleep(10)

        instance = self.get_instance(self.connection, instance_id)
        while instance.state not in "running":
            logging.warn('Waiting for instance to init')
            logging.info("Instance state:%s" % instance.state)
            time.sleep(5)
            instance = self.get_instance(self.connection, instance_id)

        logging.info("Instance state: %s" % instance.state)
        logging.info("Instance Public DNS: %s" % instance.public_dns_name)
        return instance
