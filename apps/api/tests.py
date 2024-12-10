from django.test import TestCase

from apps.api.schemas import ErrorSchema
from apps.core.shared.log import Log

log = Log()

from apps.api import testsets  # NOQA


# (Q)!: django的 TestCase 如何运行时测试？直接就行吗？python manager.py test apps.api？ -> Yes
class MainTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_main(self):
        this = self

        # (N)!: 测试发现，Schema 实例化的时候，如果传入了多余键值，会忽略掉
        schema = ErrorSchema(message="Service Unavailable. Please retry later", a=1)
        log.info(type(schema))
        log.info(schema)
        log.info(schema.dict())
