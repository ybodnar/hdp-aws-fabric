__author__ = 'yuriybodnar'

from hdpaws import Ec2Service, FabricConfigurator, AmbariService
from hdpaws.util import get_ambari_url, report

#configuration file.
import configyb as config

if __name__ == "__main__":
    service = Ec2Service(config)
    instance = service.provision_instance(config.ec2_configurations["master_node"])

    configurator = FabricConfigurator(instance, config)
    configurator.configure_networking()
    configurator.configure_root_account()
    configurator.install_ambari()
    configurator.setup_ambari()
    configurator.start_ambari()

    ambari = AmbariService(get_ambari_url(instance), config)
    ambari.register_blueprint()
    ambari.start_cluster(instance.public_dns_name)

    report(instance)
    print "Cluster configuration in progress. Please check if process finished using Ambari URL in few minutes "