#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Flickr API
# Copyright (c) 2008-2019 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from . import base

class FlickrApp(appier.WebApp):

    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(
            self,
            name = "flickr",
            *args, **kwargs
        )

    @appier.route("/", "GET")
    def index(self):
        return self.sets()

    @appier.route("/sets", "GET")
    def sets(self):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        sets = api.list_sets()
        return sets

    @appier.route("/sets/<str:id>/photos", "GET")
    def photos_set(self, id):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        photos = api.photos_set(id)
        return photos

    @appier.route("/logout", "GET")
    def logout(self):
        return self.oauth_error(None)

    @appier.route("/oauth", "GET")
    def oauth(self):
        oauth_verifier = self.field("oauth_verifier")
        appier.verify(
            oauth_verifier,
            message = "Invalid OAuth response",
            exception = appier.OperationalError
        )
        api = self.get_api()
        oauth_token, oauth_token_secret = api.oauth_access(oauth_verifier)
        self.tokens(oauth_token, oauth_token_secret, temporary = False)
        return self.redirect(
            self.url_for("flickr.index")
        )

    @appier.exception_handler(appier.OAuthAccessError)
    def oauth_error(self, error):
        self.delete()
        return self.redirect(
            self.url_for("flickr.index")
        )

    def ensure_api(self):
        oauth_token = self.session.get("fk.oauth_token", None)
        oauth_token_secret = self.session.get("fk.oauth_token_secret", None)
        oauth_temporary = self.session.get("fk.oauth_temporary", True)
        if not oauth_temporary and oauth_token and oauth_token_secret: return
        self.invalidate()
        api = base.get_api()
        url = api.oauth_authorize()
        self.tokens(api.oauth_token, api.oauth_token_secret, temporary = True)
        return url

    def get_api(self):
        oauth_token = self.session and self.session.get("fk.oauth_token", None)
        oauth_token_secret = self.session and self.session.get("fk.oauth_token_secret", None)
        api = base.get_api()
        api.oauth_token = oauth_token
        api.oauth_token_secret = oauth_token_secret
        return api

    def tokens(self, oauth_token, oauth_token_secret, temporary = True):
        self.session["fk.oauth_token"] = oauth_token
        self.session["fk.oauth_token_secret"] = oauth_token_secret
        self.session["fk.oauth_temporary"] = temporary

    def invalidate(self):
        self.tokens(None, None, temporary = True)

    def delete(self):
        if "fk.oauth_token" in self.session: del self.session["fk.oauth_token"]
        if "fk.oauth_token_secret" in self.session: del self.session["fk.oauth_token_secret"]
        if "fk.oauth_temporary" in self.session: del self.session["fk.oauth_temporary"]

if __name__ == "__main__":
    app = FlickrApp()
    app.serve()
else:
    __path__ = []
