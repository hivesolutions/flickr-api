#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Flickr API
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Flickr API.
#
# Hive Flickr API is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Flickr API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Flickr API. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import appier

from examples import base

class FlickrApp(appier.WebApp):

    def __init__(self):
        appier.WebApp.__init__(self, name = "twitter")

    @appier.route("/", "GET")
    def index(self):
        return self.me()

    @appier.route("/me", "GET")
    def me(self):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        account = api.verify_account()
        return account

    @appier.route("/streaming", "GET")
    def streaming(self):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        streaming = api.user_streaming()
        return streaming

    @appier.route("/search", "GET")
    def search(self):
        url = self.ensure_api()
        if url: return self.redirect(url)
        query = self.field("query", "Hive")
        api = self.get_api()
        results = api.tweets_search(query)
        return results

    @appier.route("/oauth", "GET")
    def oauth(self):
        oauth_verifier = self.field("oauth_verifier")
        api = self.get_api()
        oauth_token, oauth_token_secret = api.oauth_access(oauth_verifier)
        self.session["tw.oauth_token"] = oauth_token
        self.session["tw.oauth_token_secret"] = oauth_token_secret
        return self.redirect(
            self.url_for("twitter.index")
        )

    @appier.exception_handler(appier.OAuthAccessError)
    def oauth_error(self, error):
        if "tw.oauth_token" in self.session: del self.session["tw.oauth_token"]
        if "tw.oauth_token_secret" in self.session: del self.session["tw.oauth_token_secret"]
        return self.redirect(
            self.url_for("twitter.index")
        )

    def ensure_api(self):
        oauth_token = self.session.get("tw.oauth_token", None)
        oauth_token_secret = self.session.get("tw.oauth_token_secret", None)
        if oauth_token and oauth_token_secret: return
        api = base.get_api()
        url = api.oauth_authorize()
        self.session["tw.oauth_token"] = api.oauth_token
        self.session["tw.oauth_token_secret"] = api.oauth_token_secret
        return url

    def get_api(self):
        oauth_token = self.session and self.session.get("tw.oauth_token", None)
        oauth_token_secret = self.session and self.session.get("tw.oauth_token_secret", None)
        api = base.get_api()
        api.oauth_token = oauth_token
        api.oauth_token_secret = oauth_token_secret
        return api

if __name__ == "__main__":
    app = FlickrApp()
    app.serve()