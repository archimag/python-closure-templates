# -*- coding: utf-8 -*-
# 
# Copyright 2012 Moskvitin Andrey <archimag@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

import sys
import os
import os.path
from flask import Flask, send_file, Response

sys.path[0:0] = [""]

from pyclosuretempaltes.javascript_backend import compileToJS

app = Flask(__name__)

TEST_JS_DIR = os.path.join(os.path.dirname(os.path.join(os.getcwd(),  __file__)), 'js/')

@app.route('/')
def mainPage():
    return send_file(os.path.join(TEST_JS_DIR, 'index.html'))

@app.route('/closure-templates.js')
def closureTemplatesJS():
    return Response(status=200,
                    response=compileToJS(os.path.join(TEST_JS_DIR, 'template.soy')),
                    mimetype="application/javascript")

@app.route('/<path>')
def resource(path):
    return send_file(os.path.join(TEST_JS_DIR, path))

if __name__ == "__main__":
    app.debug = True
    app.run()
