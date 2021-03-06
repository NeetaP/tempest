#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import time

from tempest.common.utils import data_utils
from tempest import clients
from tempest.common import credentials
from tempest import config
from tempest import exceptions
from tempest.openstack.common import timeutils
import tempest.test

CONF = config.CONF


class BaseMonitoringTest(tempest.test.BaseTestCase):

    """Base test case class for all Monitoring API tests."""

    @classmethod
    def resource_setup(cls):
        if not CONF.service_available.monasca:
             raise cls.skipException("Monasca support is required")
        # cls.set_network_resources()
        super(BaseMonitoringTest, cls).resource_setup()
        # cls.isolated_creds = credentials.get_isolated_credentials(
        # cls.__name__, network_resources=cls.network_resources)
        cls.os = clients.Manager()

        #os = cls.get_client_manager()
        cls.monitoring_client = cls.os.monitoring_client
        # cls.servers_client = os.servers_client
        # cls.flavors_client = os.flavors_client
        # cls.image_client = os.image_client
        # cls.image_client_v2 = os.image_client_v2
        #
        # cls.nova_notifications = ['memory', 'vcpus', 'disk.root.size',
        #                           'disk.ephemeral.size']
        #
        # cls.glance_notifications = ['image.update', 'image.upload',
        #                             'image.delete']
        #
        # cls.glance_v2_notifications = ['image.download', 'image.serve']
        #
        # cls.server_ids = []
        # cls.alarm_ids = []
        cls.alarm_def_ids = []
        # cls.image_ids = []

    @classmethod
    def create_alarm_definition(cls, **kwargs):
        resp, body = cls.monitoring_client.create_alarm_definition(
            name=data_utils.rand_name('monitoring_alarm_definitions'),
            **kwargs)
        cls.alarm_def_ids.append(body['id'])
        return resp, body

    @classmethod
    def create_server(cls):
        resp, body = cls.servers_client.create_server(
            data_utils.rand_name('monasca-instance'),
            CONF.compute.image_ref, CONF.compute.flavor_ref,
            wait_until='ACTIVE')
        cls.server_ids.append(body['id'])
        return resp, body

    @classmethod
    def create_image(cls, client):
        resp, body = client.create_image(
            data_utils.rand_name('image'), container_format='bare',
            disk_format='raw', visibility='private')
        cls.image_ids.append(body['id'])
        return resp, body

    @staticmethod
    def cleanup_resources(method, list_of_ids):
        for resource_id in list_of_ids:
            try:
                method(resource_id)
            except exceptions.NotFound:
                pass

    @classmethod
    def tearDownClass(cls):
        # cls.cleanup_resources(cls.monitoring_client.delete_alarm, cls.alarm_ids)
        # cls.cleanup_resources(cls.servers_client.delete_server, cls.server_ids)
        # cls.cleanup_resources(cls.image_client.delete_image, cls.image_ids)
        # cls.clear_isolated_creds()
        super(BaseMonitoringTest, cls).tearDownClass()

    @classmethod
    def resource_cleanup(cls):
        super(BaseMonitoringTest, cls).resource_cleanup()

    def await_samples(self, metric, query):
        """
        This method is to wait for sample to add it to database.
        There are long time delays when using Postgresql (or Mysql)
        database as monasca backend
        """
        timeout = CONF.compute.build_timeout
        start = timeutils.utcnow()
        while timeutils.delta_seconds(start, timeutils.utcnow()) < timeout:
            resp, body = self.monitoring_client.list_samples(metric, query)
            self.assertEqual(resp.status, 200)
            if body:
                return resp, body
            time.sleep(CONF.compute.build_interval)

        raise exceptions.TimeoutException(
            'Sample for metric:%s with query:%s has not been added to the '
            'database within %d seconds' % (metric, query,
                                            CONF.compute.build_timeout))
