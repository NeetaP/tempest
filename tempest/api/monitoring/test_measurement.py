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

from tempest.api.monitoring import base
from tempest.common.utils import data_utils
from tempest import exceptions
from tempest import test
import datetime
import time

class MonitoringMeasurementAPITestJSON(base.BaseMonitoringTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(MonitoringMeasurementAPITestJSON, cls).setUpClass()

    @test.attr(type="gate")
    def test_measurement_default(self):
        # List metric measurement with default parameter (start_time)
        resp, body = self.monitoring_client.metric_measurement()
        self.assertEqual(200, resp.status)

    @test.attr(type="gate")
    def test_measurement_metricname(self):
        # Get version 
        metric_name = 'cpu_user_perc'
        resp, body = self.monitoring_client.metric_measurement(name=metric_name)
        self.assertEqual(200, resp.status)

    @test.attr(type="gate")
    def test_measurement_endtime(self):
        # List metric measurement with metric name
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_time = current_time.replace(' ', 'T') + 'Z'
        m_limit = 2
        resp, body = self.monitoring_client.metric_measurement(end_time=current_time, limit=str(m_limit))
        self.assertEqual(200, resp.status)

    @test.attr(type="gate")
    def test_measurement_dimension(self):
        # List metric measurement with metric name and dimension
        # Create metric with dimension
        m_name = data_utils.rand_name('metric')
        m_value = 1.0
        m_dimension = {
                      'key1': 'value1',
                      'key2': 'value2'
                      }
        m_timestamp = int(time.time() - 100)
        resp, body = self.monitoring_client.create_metric(
                     name=m_name, m_value=m_value, dimensions=m_dimension,timestamp=m_timestamp)
        self.assertEqual(204, resp.status)
        # List measurement
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_time = current_time.replace(' ', 'T') + 'Z'
        resp, body = self.monitoring_client.metric_measurement(name=m_name, dimensions=m_dimension,
                     end_time=current_time)
        self.assertEqual(200, resp.status)
