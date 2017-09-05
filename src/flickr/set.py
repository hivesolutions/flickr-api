#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Flickr API
# Copyright (c) 2008-2017 Hive Solutions Lda.
#
# This file is part of Hive Flickr API.
#
# Hive Flickr API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Flickr API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Flickr API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

class SetAPI(object):

    def list_sets(self):
        url = self.base_url + "rest"
        contents = self.get(
            url,
            method = "flickr.photosets.getList"
        )
        return contents["photosets"]["photoset"]

    def get_set(self, id):
        url = self.base_url + "rest"
        contents = self.get(
            url,
            method = "flickr.photosets.getInfo",
            photoset_id = id
        )
        return contents["photoset"]

    def photos_set(self, id, page = 1, per_page = 50):
        url = self.base_url + "rest"
        contents = self.get(
            url,
            method = "flickr.photosets.getPhotos",
            photoset_id = id,
            page = page,
            per_page = per_page
        )
        return contents["photoset"]
