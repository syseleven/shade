# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_domain
----------------------------------

Functional tests for `shade` keystone domain resource.
"""

import shade
from shade.tests import base


class TestDomain(base.TestCase):

    def setUp(self):
        super(TestDomain, self).setUp()
        self.cloud = shade.operator_cloud(cloud='devstack-admin')
        if self.cloud.cloud_config.get_api_version('identity') in ('2', '2.0'):
            self.skipTest('Identity service does not support domains')
        self.domain_prefix = self.getUniqueString('domain')
        self.addCleanup(self._cleanup_domains)

    def _cleanup_domains(self):
        exception_list = list()
        for domain in self.cloud.list_domains():
            if domain['name'].startswith(self.domain_prefix):
                try:
                    self.cloud.delete_domain(domain['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise shade.OpenStackCloudException('\n'.join(exception_list))

    def test_search_domains(self):
        domain_name = self.domain_prefix + '_search'

        # Shouldn't find any domain with this name yet
        results = self.cloud.search_domains(filters=dict(name=domain_name))
        self.assertEqual(0, len(results))

        # Now create a new domain
        domain = self.cloud.create_domain(domain_name)
        self.assertEqual(domain_name, domain['name'])

        # Now we should find only the new domain
        results = self.cloud.search_domains(filters=dict(name=domain_name))
        self.assertEqual(1, len(results))
        self.assertEqual(domain_name, results[0]['name'])

    def test_update_domain(self):
        domain = self.cloud.create_domain(self.domain_prefix, 'description')
        self.assertEqual(self.domain_prefix, domain['name'])
        self.assertEqual('description', domain['description'])
        self.assertTrue(domain['enabled'])
        updated = self.cloud.update_domain(domain['id'], name='updated name',
                                           description='updated description',
                                           enabled=False)
        self.assertEqual('updated name', updated['name'])
        self.assertEqual('updated description', updated['description'])
        self.assertFalse(updated['enabled'])
