__author__ = 'yuriybodnar'

import requests, json
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class AmbariService():
    def __init__(self, url, config):
        self.headers = {"X-Requested-By": "ambari"}
        self.credentials = ("admin", "admin")
        self.url = url
        self.config = config

    def get_blueprint(self):
        file = open(self.config.ambari_blueprint_file, "r")
        res = file.readlines()
        return ''.join(res)


    def get_cluster_definition(self, hostname, cluster_file=None):
        file = open(self.config.ambari_cluster_file if cluster_file is None else cluster_file, "r")
        res = file.readlines()
        return ''.join(res).replace("PARAM_HOST_NAME", hostname)


    def register_blueprint(self, blueprint=None, blueprint_name="single-node-hdfs-yarn"):
        if blueprint is None:
            blueprint = self.get_blueprint()
        service = "api/v1/blueprints/{blueprint_name}".format(blueprint_name=blueprint_name)
        logger.info("Sending blueprint")
        logger.debug(blueprint)
        response = requests.post('/'.join([self.url, service]),
                                 json=blueprint, auth=self.credentials,
                                 headers=self.headers)
        status = response.status_code
        if status != 201:
            logger.error(status)
            logger.error(response.text)
        else:
            logger.info("Registered blueprint successfully")

    def register_cluster(self, cluster, cluster_name="TestCluster"):
        service = "api/v1/clusters/{cluster_name}".format(cluster_name=cluster_name)
        logger.info("Registering cluster")
        logger.debug("Sending cluster configuration")
        logger.debug(cluster)
        response = requests.post('/'.join([self.url, service]),
                                 json=cluster, auth=self.credentials,
                                 headers=self.headers)
        status = response.status_code
        if status != 201:
            logger.error(response.status_code)
            logger.error(response.text)
        else:
            logger.info("Successfully registered cluster")

    def start_cluster(self, hostname):
        logger.info("Starting cluster")
        cluster_def = self.get_cluster_definition(hostname)
        self.register_cluster(cluster_def)

# if __name__ == "__main__":
    import configyb
    # ambari = AmbariService("http://ec2-54-152-83-80.compute-1.amazonaws.com:8080", configyb)
    # # ambari.register_blueprint()
    # ambari.register_cluster(ambari.get_cluster("ip-172-30-0-124.ec2.internal"))
