from django.test import TestCase

from ninja.testing import TestClient

from apps.api.routersets.chatgpt import router


class Tester(TestCase):
    # 2024-12-14：主要是冒烟测试，正确的输入拿到 200 响应即可。我的精力也就只能做到冒烟测试了。
    #   题外话，请保证，只要是正确的响应就是 200，其余情况都不等于 200！！！
    #       比如：_get_ai_event_steam_response 函数里面就不对！明明超时了还是返回 200！
    def setUp(self):
        self.client = TestClient(router)

    def test_ask_english_ai(self):
        response = self.client.post("ask_english_ai", data={
            "prompt": "hello"
        })
        self.assertEqual(response.status_code, 200)
