import logging
log = logging.getLogger(__name__)
import keystoneclient.v2_0.client as ksclient


class Identity:
    ''' Wrapper to the OpenStack Identity service (Keystone) '''
    def __init__(self, conf):
        creds = self._get_creds(conf)
        self.keystone = ksclient.Client(**creds)

    def _get_creds(self, conf):
        d = {}
        d['username'] = conf.get("environment", "OS_USERNAME")
        d['password'] = conf.get("environment", "OS_PASSWORD")
        d['auth_url'] = conf.get("environment", "OS_AUTH_URL")
        d['tenant_name'] = conf.get("environment", "OS_TENANT_NAME")
        return d

    def _tenant2dict(self, tenant):
        d = {}
        d["enabled"] = tenant.enabled
        d['description'] = tenant.description
        d["name"] = tenant.name
        d["id"] = tenant.id
        return d

    def list_tenants(self):
        ''' Returns a list of dictionaries, one for each project. '''
        ks_tenants = self.keystone.tenants.list()
        return [self._tenant2dict(x) for x in ks_tenants]
