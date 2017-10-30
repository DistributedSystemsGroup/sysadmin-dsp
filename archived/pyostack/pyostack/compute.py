import novaclient.v1_1.client as nvclient
import novaclient.exceptions
import logging
log = logging.getLogger(__name__)


class Compute:
    ''' Wrapper for the Openstack Compute service (Nova) '''
    def __init__(self, conf):
        creds = self._get_creds(conf)
        self.nova = nvclient.Client(**creds)

    def _get_creds(self, conf):
        d = {}
        d['username'] = conf.get("environment", "OS_USERNAME")
        d['api_key'] = conf.get("environment", "OS_PASSWORD")
        d['auth_url'] = conf.get("environment", "OS_AUTH_URL")
        d['project_id'] = conf.get("environment", "OS_TENANT_NAME")
        return d

    def server_create(self, name, flavor, image, host, key):
        ''' Start a new server '''
        if not self.nova.keypairs.findall(name=key):
            raise RuntimeError("SSH key %s not found" % key)
        image = self.nova.images.find(name=image)
        flavor = self.nova.flavors.find(name=flavor)
        instance = self.nova.servers.create(name=name,
                                            image=image,
                                            flavor=flavor,
                                            key_name=key,
                                            availability_zone=host)
        return instance

    def server_refresh(self, instance):
        ''' Refresh an instance object obtained by server_create or
        server_find*. Needed to update, for example, the status attribute. '''
        return self.nova.servers.get(instance.id)

    def server_find_by_name(self, name):
        ''' Return the instance object for the server named 'name' '''
        try:
            return self.nova.servers.find(name=name)
        except novaclient.exceptions.NotFound:
            return None

    def server_delete(self, instance):
        ''' Terminate an instance '''
        instance.delete()

    def server_list(self, all_tenants=False):
        ''' Return a list of all servers for the current tenant.
        If the all_tenants parameter is set to True, will return server for
        all tenants '''
        return self.nova.servers.list(search_opts={'all_tenants': 1})

    def get_floating_ip(self, instance):
        ''' Returns the floating IP for an instance. If that instance does
        not have one assigned, it will be created and assigned. '''
        flips = self.nova.floating_ips.list()
        unused = []
        for addr in flips:
            if addr.instance_id == instance.id:
                return addr.ip
            if addr.instance_id is None:
                unused.append(addr)
        if len(unused) == 0:
            log.info("Creating new floating IP address")
            addr = self.nova.floating_ips.create()
            unused.append(addr)
        addr = unused.pop()
        log.info("Associating floating IP to VM '%s'" % instance.name)
        instance.add_floating_ip(addr)
        return addr.ip

    def get_private_ip(self, instance):
        '''Returns the first network list of addresses'''
        for net in instance.networks:
            return instance.networks[net]

    def get_vcpu_count(self, instance):
        '''Returns the number of VCPUs configured for an instance'''
        flavor_id = instance.flavor["id"]
        fl = self.nova.flavors.find(id=flavor_id)
        return fl.vcpus

    def get_mem_size(self, instance):
        '''Returns the number of VCPUs configured for an instance'''
        flavor_id = instance.flavor["id"]
        fl = self.nova.flavors.find(id=flavor_id)
        return fl.ram * 1024 * 1024
