__copyright__ = '''
Copyright 2018 the original author or authors.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
__author__ = 'David Turanski'

import grpc
import unittest
import subprocess
import os
import uuid
import time

from invoker import function_pb2_grpc as function
from invoker import function_pb2 as message

# TODO: Make this portable
PYTHON2 = "~/miniconda2/bin/python"

class GrpcFunctionTest(unittest.TestCase):
    """
    Assumes os.getcwd() is the project base directory
    """
    @classmethod
    def setUpClass(cls):
        # TODO: Make this portable
        cls.workingdir = os.path.abspath("./invoker")
        cls.command = "%s funcrunner.py" % PYTHON2

    def setUp(self):
        pass

    def tearDown(self):
        print("killing %s" % self.process.pid)
        self.process.kill()

    def test_upper(self):
        port = find_free_port()
        env = {
            'PYTHONPATH': '%s/tests/functions:$PYTHONPATH' % os.getcwd(),
            'GRPC_PORT': str(port),
            'FUNCTION_URI': 'file://%s/tests/functions/upper.py?handler=handle' % os.getcwd()
        }

        self.process = subprocess.Popen(self.command,
                                        cwd=self.workingdir,
                                        shell=True,
                                        env=env,
                                        preexec_fn=os.setsid,
                                        )
        time.sleep(0.5)

        channel = grpc.insecure_channel('localhost:%s' % port)
        self.stub = function.MessageFunctionStub(channel)

        def generate_messages():
            headers = {
                'Content-Type': message.Message.HeaderValue(values=['text/plain']),
                'correlationId': message.Message.HeaderValue(values=[str(uuid.uuid4())])
            }

            messages = [
                message.Message(payload="hello", headers=headers),
                message.Message(payload="world", headers=headers),
                message.Message(payload="foo", headers=headers),
                message.Message(payload="bar", headers=headers),
            ]
            for msg in messages:
                yield msg

        responses = self.stub.Call(generate_messages())
        expected = ['HELLO', 'WORLD', 'FOO', 'BAR']

        for response in responses:
            self.assertTrue(response.payload in expected)
            expected.remove(response.payload)

        self.assertEquals(0, len(expected))

    def test_concat(self):
        port = find_free_port()
        env = {
            'PYTHONPATH': '%s/tests/functions:$PYTHONPATH' % os.getcwd(),
            'GRPC_PORT': str(port),
            'FUNCTION_URI': 'file://%s/tests/functions/concat.py?handler=concat' % os.getcwd()
        }

        self.process = subprocess.Popen(self.command,
                                        cwd=self.workingdir,
                                        shell=True,
                                        env=env,
                                        preexec_fn=os.setsid,
                                        )
        time.sleep(0.5)

        channel = grpc.insecure_channel('localhost:%s' % port)
        self.stub = function.MessageFunctionStub(channel)

        def generate_messages():
            headers = {
                'Content-Type': message.Message.HeaderValue(values=['application/json']),
                'correlationId': message.Message.HeaderValue(values=[str(uuid.uuid4())])
            }

            messages = [
                message.Message(payload='{"foo":"bar","hello":"world"}', headers=headers),
            ]
            for msg in messages:
                yield msg

        responses = self.stub.Call(generate_messages())

        for response in responses:
            self.assertEquals('{"result": "foobarhelloworld"}', response.payload)

    def test_accepts_application_json(self):
        port = find_free_port()
        env = {
            'PYTHONPATH': '%s/tests/functions:$PYTHONPATH' % os.getcwd(),
            'GRPC_PORT': str(port),
            'FUNCTION_URI': 'file://%s/tests/functions/concat.py?handler=concat' % os.getcwd()
        }

        self.process = subprocess.Popen(self.command,
                                        cwd=self.workingdir,
                                        shell=True,
                                        env=env,
                                        preexec_fn=os.setsid,
                                        )
        time.sleep(0.5)

        channel = grpc.insecure_channel('localhost:%d' % port)
        self.stub = function.MessageFunctionStub(channel)

        def generate_messages():
            headers = {
                'Content-Type': message.Message.HeaderValue(values=['application/json']),
                'Accept': message.Message.HeaderValue(values=['application/json']),
                'correlationId': message.Message.HeaderValue(values=[str(uuid.uuid4())])
            }

            messages = [
                message.Message(payload='{"foo":"bar","hello":"world"}', headers=headers),
            ]
            for msg in messages:
                yield msg

        responses = self.stub.Call(generate_messages())

        for response in responses:
            self.assertEquals('{"result": "foobarhelloworld"}', response.payload)

    def test_accepts_text_plain(self):
        port = find_free_port()
        env = {
            'PYTHONPATH': '%s/tests/functions:$PYTHONPATH' % os.getcwd(),
             'GRPC_PORT': str(port),
            'FUNCTION_URI': 'file://%s/tests/functions/concat.py?handler=concat' % os.getcwd()
        }

        self.process = subprocess.Popen(self.command,
                                        cwd=self.workingdir,
                                        shell=True,
                                        env=env,
                                        preexec_fn=os.setsid,
                                        )
        time.sleep(0.5)

        channel = grpc.insecure_channel('localhost:%d' % port)
        self.stub = function.MessageFunctionStub(channel)

        def generate_messages():
            headers = {
                'Content-Type': message.Message.HeaderValue(values=['application/json']),
                'Accept': message.Message.HeaderValue(values=['text/plain']),
                'correlationId': message.Message.HeaderValue(values=[str(uuid.uuid4())])
            }

            messages = [
                message.Message(payload='{"foo":"bar","hello":"world"}', headers=headers),
            ]
            for msg in messages:
                yield msg

        responses = self.stub.Call(generate_messages())

        for response in responses:
            self.assertEquals('{"result": "foobarhelloworld"}', response.payload)

    def test_accepts_not_supported(self):
        port = find_free_port()
        env = {
            'PYTHONPATH': '%s/tests/functions:$PYTHONPATH' % os.getcwd(),
            'GRPC_PORT': str(port),
            'FUNCTION_URI': 'file://%s/tests/functions/concat.py?handler=concat' % os.getcwd()
        }

        self.process = subprocess.Popen(self.command,
                                        cwd=self.workingdir,
                                        shell=True,
                                        env=env,
                                        preexec_fn=os.setsid,
                                        )
        time.sleep(0.5)

        channel = grpc.insecure_channel('localhost:%s' % port)
        self.stub = function.MessageFunctionStub(channel)

        def generate_messages():
            headers = {
                'Content-Type': message.Message.HeaderValue(values=['application/json']),
                'Accept': message.Message.HeaderValue(values=['application/xml']),
                'correlationId': message.Message.HeaderValue(values=[str(uuid.uuid4())])
            }

            messages = [
                message.Message(payload='{"foo":"bar","hello":"world"}', headers=headers),
            ]
            for msg in messages:
                yield msg

        try:
            responses = self.stub.Call(generate_messages())
            self.assertEquals(grpc._channel._Rendezvous, type(responses))
            #TODO: Investigate error handling
        except RuntimeError:
            pass



import socket
from contextlib import closing

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]
