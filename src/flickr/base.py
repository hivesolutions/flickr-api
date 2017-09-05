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

import json

import appier

from . import set

BASE_URL = "https://www.flickr.com/services/"
""" The default base url to be used when no other
base url value is provided to the constructor """

CLIENT_KEY = None
""" The default value to be used for the client key
in case no client key is provided to the api client """

CLIENT_SECRET = None
""" The secret value to be used for situations where
no client secret has been provided to the client """

REDIRECT_URL = "http://localhost:8080/oauth"
""" The redirect url used as default (fallback) value
in case none is provided to the api (client) """

class API(
    appier.OAuth1API,
    set.SetAPI
):
    """
    Implementation of the basic Flickr API according to the
    definition in the website. The authentication mechanism
    used is OAuth1.0a and the underlying serialization process
    is JSON (for simplicity reasons).

    Some of the implementation details required some hacks in
    order to overcome some of the limitations in the API.

    :see: https://www.flickr.com/services/api
    """

    def __init__(self, *args, **kwargs):
        appier.OAuth1API.__init__(self, *args, **kwargs)
        self.client_key = appier.conf("FLICKR_KEY", CLIENT_KEY)
        self.client_secret = appier.conf("FLICKR_SECRET", CLIENT_SECRET)
        self.redirect_url = appier.conf("FLICKR_REDIRECT_URL", REDIRECT_URL)
        self.base_url = kwargs.get("base_url", BASE_URL)
        self.client_key = kwargs.get("client_key", self.client_key)
        self.client_secret = kwargs.get("client_secret", self.client_secret)
        self.redirect_url = kwargs.get("redirect_url", self.redirect_url)
        self.oauth_token = kwargs.get("oauth_token", None)
        self.oauth_token_secret = kwargs.get("oauth_token_secret", None)

    def request(self, method, *args, **kwargs):
        try: result = method(*args, **kwargs)
        except appier.HTTPError as exception:
            self.handle_error(exception)
        else:
            try: return self.try_json(result)
            except ValueError: return result

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        appier.OAuth1API.build(self, method, url, headers, kwargs)
        if not method == "GET": return
        format = kwargs.get("format", "json")
        kwargs["format"] = format

    def try_json(self, result):
        is_bytes = appier.legacy.is_bytes(result)
        if is_bytes: result = result.decode("utf-8")
        result = json.loads(result[14:-1])
        is_fail = result.get("stat", None) == "fail"
        if is_fail: raise appier.OAuthAccessError(
            message = result.get("message", "Problem in flickr api message")
        )
        return result

    def oauth_request(self, state = None):
        url = self.base_url + "oauth/request_token"
        redirect_url = self.redirect_url
        if state: redirect_url += "?state=%s" % appier.quote(state, safe = "~")
        contents = self.post(url, oauth_callback = redirect_url)
        contents = contents.decode("utf-8")
        contents = appier.legacy.parse_qs(contents)
        self.oauth_token = contents["oauth_token"][0]
        self.oauth_token_secret = contents["oauth_token_secret"][0]

    def oauth_authorize(self, state = None):
        self.oauth_request(state = state)
        url = self.base_url + "oauth/authorize"
        values = dict(
            oauth_token = self.oauth_token
        )
        data = appier.legacy.urlencode(values)
        url = url + "?" + data
        return url

    def oauth_access(self, oauth_verifier = None):
        url = self.base_url + "oauth/access_token"
        kwargs = dict()
        if oauth_verifier: kwargs["oauth_verifier"] = oauth_verifier
        contents = self.post(url, **kwargs)
        contents = contents.decode("utf-8")
        contents = appier.legacy.parse_qs(contents)
        self.oauth_token = contents["oauth_token"][0]
        self.oauth_token_secret = contents["oauth_token_secret"][0]
        self.trigger("oauth_token", self.oauth_token)
        return (self.oauth_token, self.oauth_token_secret)
