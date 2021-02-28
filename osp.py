import glanceclient.v2.client as glclient
from os import getenv
from novaclient.client import Client
from keystoneauth1 import session
from keystoneauth1.identity import v3


class Credentials:
    def __init__(self):
        self.osp_username = getenv("OS_USERNAME")
        self.osp_password = getenv("OS_PASSWORD")
        self.osp_auth_url = getenv("OS_AUTH_URL")
        self.osp_service_region = getenv("OS_REGION_NAME")
        self.osp_project_id = getenv("OS_PROJECT_ID")
        self.osp_project_name = getenv("OS_PROJECT_NAME")
        self.osp_user_domain_name = getenv("OS_USER_DOMAIN_NAME")
        self.osp_project_domain_id = getenv("OS_PROJECT_DOMAIN_ID")
        self.osp_identity_api_version = getenv("OS_IDENTITY_API_VERSION")

        if not self.osp_username:
            raise Exception("Missing OS_USERNAME")

        if not self.osp_password:
            raise Exception("Missing OS_PASSWORD")

        if not self.osp_auth_url:
            raise Exception("Missing OS_AUTH_URL")

        if not self.osp_service_region:
            raise Exception("Missing OS_REGION_NAME")

        if not self.osp_project_id:
            raise Exception("Missing OS_PROJECT_ID")

        if not self.osp_project_name:
            raise Exception("Missing OS_PROJECT_NAME")

        if not self.osp_user_domain_name:
            raise Exception("Missing OS_USER_DOMAIN_NAME")

        if not self.osp_project_domain_id:
            raise Exception("Missing OS_PROJECT_DOMAIN_ID")

        if not self.osp_identity_api_version:
            raise Exception("Missing OS_IDENTITY_API_VERSION")


class OpenstackSDK(object):
    def __init__(self):
        self.creds = Credentials()
        self.auth = v3.Password(auth_url=self.creds.osp_auth_url,
                                project_id=self.creds.osp_project_id,
                                project_name=self.creds.osp_project_name,
                                user_domain_name=self.creds.osp_user_domain_name,
                                project_domain_id=self.creds.osp_project_domain_id,
                                username=self.creds.osp_username,
                                password=self.creds.osp_password)

        self.session = session.Session(auth=self.auth)
        self.nova = Client('2', session=self.session)
        self.glance = glclient.Client('2', session=self.session)

    def get_all_instances(self):
        try:
            rs = self.nova.servers.list()
            vm_list = []
            for vm in rs:
                name = None
                image = None
                created_at = None
                flavor = None
                vm_id = None

                if "id" in vm.image:
                    # situation when image is deleted but there are vms
                    # with that image associated. e.g.: vm1 is provisioned
                    # with image1 then image1 is deleted from tenant
                    # or from public
                    try:
                        os_img = self.glance.images.get(vm.image['id'])
                        image = os_img['name']
                    except Exception as ex:
                        print(ex)
                        image = "NA, prev deleted"

                if vm.name and vm.name is not None:
                    name = vm.name

                if vm.created and vm.created is not None:
                    created_at = vm.created

                if vm.flavor and "id" in vm.flavor is not None:
                    flavor = vm.flavor['id']

                if vm.id and vm.id is not None:
                    vm_id = vm.id

                instance = {'name': name,
                            'image': image,
                            'created_at': created_at,
                            'flavor': flavor,
                            'ip': self.get_server_ip(vm),
                            'id': vm_id,
                            'obj': vm
                            }
                vm_list.append(instance)
        except Exception as ex:
            print(ex)
            if vm:
                print(f"WARN: check this vm {vm}")
            raise (ex)
        return vm_list

    def delete_instance(self, vm):
        """delete openstack instance"""
        try:
            self.nova.servers.delete(vm['obj'])
            return True
        except Exception as ex:
            print(ex)

    def get_server_ip(self, server):
        """get network IP for a given server object"""
        if len(server.addresses) == 0:
            return None
        network = list(server.addresses)[0]
        return server.networks[network][0]

    def get_zoombies_floating_ips(self):
        """get all floating ips and filter by disassociated ips"""
        all_floating_ips = self.neutron.list_floatingips()
        zoombies = []
        for fip in all_floating_ips['floatingips']:
            if not fip['port_id'] and not fip['router_id']:
                zoombies.append(fip)
        return zoombies

    def delete_floating_ip(self, ip):
        """delete openstack instance"""
        try:
            self.neutron.delete_floatingip(ip)
            return True
        except Exception as ex:
            print(ex)
