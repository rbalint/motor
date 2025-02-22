# Copyright 2018-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

import collections
import os
import re

from bson import json_util
from bson.json_util import JSONOptions
from pymongo.read_concern import ReadConcern
from pymongo.results import (BulkWriteResult,
                             InsertManyResult,
                             InsertOneResult,
                             UpdateResult, DeleteResult)

from motor.motor_tornado import (MotorCommandCursor,
                                 MotorCursor,
                                 MotorLatentCommandCursor)
from test.utils import TestListener

from test.version import Version

"""Test Motor, an asynchronous driver for MongoDB and Tornado."""

import unittest

from pymongo import (ReadPreference,
                     WriteConcern)
from tornado.testing import gen_test

from test.test_environment import env
from test.tornado_tests import MotorTest


class TestTransactionsConvenientAPI(MotorTest):

    @env.require_transactions
    @gen_test
    async def test_basic(self):
        # Create the collection.
        await self.collection.insert_one({})

        async def coro(session):
            await self.collection.insert_one({'_id': 1}, session=session)

        async with await self.cx.start_session() as s:
            await s.with_transaction(coro,
                                     read_concern=ReadConcern('local'),
                                     write_concern=WriteConcern('majority'),
                                     read_preference=ReadPreference.PRIMARY,
                                     max_commit_time_ms=30000)

        doc = await self.collection.find_one({'_id': 1})
        self.assertEqual(doc, {'_id': 1})


if __name__ == '__main__':
    unittest.main()
