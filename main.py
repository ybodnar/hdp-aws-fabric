__author__ = 'yuriybodnar'

from hdpaws import Ec2Service, FabricConfigurator, AmbariService
from hdpaws.util import get_ambari_url, report

# use config.py.template to create your own config
import configyb as config
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    service = Ec2Service(config)
    instance = service.provision_instance(config.ec2_configurations["master_node"])

    configurator = FabricConfigurator(instance, config)
    configurator.configure_networking()
    configurator.configure_root_account()
    configurator.install_ambari_server()
    configurator.setup_ambari_server()
    configurator.start_ambari_server()

    configurator.install_ambari_agent()
    configurator.setup_ambari_agent(instance.private_dns_name)
    configurator.start_ambari_agent()

    ambari = AmbariService(get_ambari_url(instance), config)
    ambari.register_blueprint()
    ambari.start_cluster(instance.private_dns_name)

    report(instance, config)
    logging.warning(
        "Cluster configuration in progress. Please check if process finished using Ambari URL in few minutes")