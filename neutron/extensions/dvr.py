# Copyright (c) 2014 OpenStack Foundation.  All rights reserved.
#
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

import abc

import six

from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.common import constants
from neutron.common import exceptions
from neutron import manager

RESOURCE_NAME = 'dvr_mac_binding'
RESOURCE_ATTRIBUTE_MAP = {
    RESOURCE_NAME + 's' : {
        'mac_address': {'allow_post': False, 'allow_put': False,
                        'validate': {'type:mac_address': None},
                        'is_visible': True,
                        'primary_key': True
                       },
        'name': {'allow_post': True, 'allow_put': False,
                 'is_visible': True, 'default': '',
                 'validate': {'type:hostname': None}
                }
    }
}

DISTRIBUTED = 'distributed'
EXTENDED_ATTRIBUTES_2_0 = {
    'routers': {
        DISTRIBUTED: {'allow_post': True,
                      'allow_put': True,
                      'is_visible': True,
                      'default': attr.ATTR_NOT_SPECIFIED,
                      'convert_to': attr.convert_to_boolean_if_not_none,
                      'enforce_policy': True},
    }
}

class DVRMacAddressNotFound(exceptions.NotFound):
    message = _("Distributed Virtual Router Mac Address for "
                "host %(host)s does not exist.")


class MacAddressGenerationFailure(exceptions.ServiceUnavailable):
    message = _("Unable to generate unique DVR mac for host %(host)s.")


class Dvr(object):
    """Extension class supporting distributed virtual router."""

    @classmethod
    def get_name(cls):
        return "Distributed Virtual Router"

    @classmethod
    def get_alias(cls):
        return constants.L3_DISTRIBUTED_EXT_ALIAS

    @classmethod
    def get_description(cls):
        return "Enables configuration of Distributed Virtual Routers."

    @classmethod
    def get_namespace(cls):
        return ("http://docs.openstack.org/ext/"
                "%s/api/v1.0" % constants.L3_DISTRIBUTED_EXT_ALIAS)

    @classmethod
    def get_updated(cls):
        return "2014-06-1T10:00:00-00:00"

    def get_required_extensions(self):
        return ["router"]

    @classmethod
    def get_resources(cls):
        """Returns Ext Resources."""
        my_plurals = [(key, key[:-2]) for key in RESOURCE_ATTRIBUTE_MAP.keys()]
        attr.PLURALS.update(dict(my_plurals))
        plugin = manager.NeutronManager.get_plugin()
        params = RESOURCE_ATTRIBUTE_MAP.get(RESOURCE_NAME + 's')
        controller = base.create_resource(RESOURCE_NAME + 's',
                                          RESOURCE_NAME,
                                          plugin, params
                                          )

        ex = extensions.ResourceExtension(RESOURCE_NAME + 's',
                                          controller)

        return [ex]

    def get_extended_resources(self, version):
        if version == "2.0":
            return EXTENDED_ATTRIBUTES_2_0
        else:
            return {}


@six.add_metaclass(abc.ABCMeta)
class DVRMacAddressPluginBase(object):

    @abc.abstractmethod
    def get_dvr_mac_bindings(self, context, filters=None, fields=None,
                            sorts=None, limit=None, marker=None,
                            page_reverse=False):
        """ Get DVR MAC Address Bindings

        Return a list of host to mac address bindings
        """
        pass

    @abc.abstractmethod
    def create_dvr_mac_binding(self, context, dvr_mac_binding):
        """ Create DVR Mac Address Binding

        Given a hostname, create a new DVR Mac address binding
        """
        pass

    @abc.abstractmethod
    def delete_dvr_mac_binding(self, context, mac_address):
        """ Delete a DVR Mac Address Binding """
        pass

    @abc.abstractmethod
    def delete_dvr_mac_address(self, context, host):
        pass

    @abc.abstractmethod
    def get_dvr_mac_address_list(self, context):
        pass

    @abc.abstractmethod
    def get_dvr_mac_address_by_host(self, context, host):
        pass
