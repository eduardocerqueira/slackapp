import pytest
from osp import OpenstackSDK


class TestInstances(object):

    def test_get_all_instances(self):
        openstack = OpenstackSDK()
        if openstack.get_all_instances():
            assert True
        else:
            assert False
