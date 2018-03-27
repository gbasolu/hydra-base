#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) Copyright 2013 to 2017 University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#

import server
from fixtures import *
import pytest
import hydra_base as hb
from hydra_base.lib.objects import JSONObject

import logging
log = logging.getLogger(__name__)

class TestGroup:
    """
        Test for network-based functionality
    """
    # Todo make this a fixture?
    user_id = util.user_id

    def test_get_resourcegroup(self, session, network_with_data):
        network = network_with_data
        group = network.resourcegroups[0]
        s = network.scenarios[0]

        resourcegroup_without_data = hb.get_resourcegroup(group.group_id)

        for ra in resourcegroup_without_data.attributes:
            assert not hasattr(ra, 'resourcescenario')

        resourcegroup_with_data = hb.get_resourcegroup(group.group_id, s.scenario_id, user_id=self.user_id)

        attrs_with_data = []
        for ra in resourcegroup_with_data.attributes:
            if hasattr(ra, 'resourcescenario'):
                if ra.resourcescenario:
                    attrs_with_data.append(ra.resource_attr_id)
        assert len(attrs_with_data) > 0

        group_items = hb.get_resourcegroupitems(group.group_id, s.scenario_id, user_id=self.user_id)
        assert len(group_items) > 0

    def test_add_resourcegroup(self, session, network_with_data):

        network = network_with_data

        group = JSONObject({})
        group.network_id=network.id
        group.id = -1
        group.name = 'test new group'
        group.description = 'test new group'

        template_id = network.types[0].template_id
        template = JSONObject(hb.get_template(template_id, user_id=self.user_id))

        type_summary_arr = []

        type_summary      = JSONObject({})
        type_summary.id   = template.id
        type_summary.name = template.name
        type_summary.id   = template.templatetypes[2].id
        type_summary.name = template.templatetypes[2].name

        type_summary_arr.append(type_summary)

        group.types = type_summary_arr

        new_group = hb.add_group(network.id, group, user_id=self.user_id)

        group_attr_ids = []
        for resource_attr in new_group.attributes:
            group_attr_ids.append(resource_attr.attr_id)

        for typeattr in template.templatetypes[2].typeattrs:
            assert typeattr.attr_id in group_attr_ids

        new_network = hb.get_network(network.id, user_id=self.user_id)

        assert len(new_network.resourcegroups) == len(network.resourcegroups)+1; "new resource group was not added correctly"

    def test_add_resourcegroupitem(self, session, network_with_extra_group):

        network = network_with_extra_group

        scenario = network.scenarios[0]

        group    = network.resourcegroups[-1]
        node_id = network.nodes[0].node_id

        item = JSONObject({})
        item.ref_key = 'NODE'
        item.ref_id  = node_id
        item.group_id = group.group_id

        new_item = hb.add_resourcegroupitem(item, scenario.scenario_id, user_id=self.user_id)

        assert new_item.node_id == node_id


    def test_set_group_status(self, session, network_with_extra_group):
        net = network_with_extra_group 

        group_to_delete = net.resourcegroups[0]

        hb.set_group_status(group_to_delete.group_id, 'X', user_id=self.user_id)

        updated_net = hb.get_network(net.id, user_id=self.user_id)

        group_ids = []
        for g in updated_net.resourcegroups:
            group_ids.append(g.group_id)

        assert group_to_delete.id not in group_ids

        hb.set_group_status(group_to_delete.group_id, 'A', user_id=self.user_id)

        updated_net = hb.get_network(net.id, user_id=self.user_id)

        group_ids = []
        for g in updated_net.resourcegroups:
            group_ids.append(g.group_id)

        assert group_to_delete.group_id in group_ids


    def test_purge_group(self, session, network_with_extra_group):
        net = network_with_extra_group 
        scenario_id = net.scenarios[0].id
        group_id_to_delete = net.resourcegroups[-1].group_id
        group_id_to_keep = net.resourcegroups[0].group_id

        group_datasets = hb.get_resource_data('GROUP', group_id_to_delete, scenario_id)
        log.info("Deleting group %s", group_id_to_delete)

        hb.delete_resourcegroup(group_id_to_delete, user_id=self.user_id)

        updated_net = JSONObject(hb.get_network(net.id, 'Y', user_id=self.user_id))
        assert len(updated_net.resourcegroups) == 1
        assert updated_net.resourcegroups[0].group_id == group_id_to_keep

        for rs in group_datasets:
            #In these tests, all timeseries are unique to their resources,
            #so after removing the group no timeseries to which it was attached
            #should still exist.
            d = rs.value
            with pytest.raises(hb.HydraError):
                if d.type == 'timeseries':
                    hb.get_dataset(d.dataset_id)


if __name__ == '__main__':
    server.run()
