#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import re

# ================= /
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("Hello, Udacity")

# ================= /lesson2/rot13
htmlrot13 = """
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Rot 13</title>
  </head>

  <body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text" style="height: 100px; width: 400px;">%(text)s</textarea>
      <br>
      <input type="submit">
    </form>
  </body>

</html>
"""

class Lesson2Handler(webapp2.RequestHandler):
    def get(self):
        self.response.write(htmlrot13 % {"text": ""})

    def post(self):
        text = self.request.get('text')
        newtext = ''
        for char in text:
            if char >= 'a' and char <= 'z':
                orde = ord(char)
                orde += 13
                if orde > ord('z'):
                    orde -= 26
                char = chr(orde)
            elif char >= 'A' and char <= 'Z':
                orde = ord(char)
                orde += 13
                if orde > ord('Z'):
                    orde -= 26
                char = chr(orde)
            newtext += char

        self.response.write(htmlrot13 % {"text": cgi.escape(newtext)})

# ================= /lesson2/signup
HTML_SIGNUP = """
<!DOCTYPE html>

<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>

  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="%(username)s">
          </td>
          <td class="error">%(username_error)s</td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="">
          </td>
          <td class="error">%(password_error)s</td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="">
          </td>
          <td class="error">%(verify_error)s</td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="%(email)s">
          </td>
          <td class="error">%(email_error)s</td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>
"""

class Lesson2bHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(HTML_SIGNUP % {
            "username": "", "username_error": "",
            "password": "", "password_error": "",
            "verify": "", "verify_error": "",
            "email": "", "email_error": ""})

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        valid = True

        username_error = self.checkusername(username)
        password_error = self.checkpassword(password)
        verify_error = self.checkverify(password, verify)
        email_error = self.checkemail(email)
        valid = len(username_error) == 0 and len(password_error) == 0 \
            and len(verify_error) == 0 and len(email_error) == 0

        if valid:
            self.redirect("/lesson2/success?username="+username)
        else:
            self.response.write(HTML_SIGNUP % {
            "username": cgi.escape(username), "username_error": username_error,
            "password": cgi.escape(password), "password_error": password_error,
            "verify": cgi.escape(verify), "verify_error": verify_error,
            "email": cgi.escape(email), "email_error": email_error})

    def checkusername(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        if USER_RE.match(username):
            return ""
        else:
            return "That's not a valid username."

    def checkpassword(self, password):
        PASS_RE = re.compile(r"^.{3,20}$")
        if PASS_RE.match(password):
            return ""
        else:
            return "That wasn't a valid password."

    def checkverify(self, password, verify):
        if len(password) == 0 or verify == password:
            return ""
        else:
            return "Your passwords didn't match."

    def checkemail(self, email):
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        if len(email) == 0 or EMAIL_RE.match(email):
            return ""
        else:
            return "That's not a valid email."

# ================= /lesson2/success
class Lesson2bSuccessHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.get("username")
        self.response.write("Welcome, "+cgi.escape(username))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/lesson2/rot13', Lesson2Handler),
    ('/lesson2/signup', Lesson2bHandler),
    ('/lesson2/success', Lesson2bSuccessHandler)
], debug=True)
