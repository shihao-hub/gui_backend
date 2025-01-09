import ssl

import aiohttp
import asyncio

"""
    ### 注意事项
    - **安全风险**：取消 SSL 验证会使得中间人攻击（Man-in-the-Middle Attack）更容易发生，严重降低了数据传输的安全性 。因此，仅在非常有必要的测试环境中使用此配置，不建议在生产环境中使用。
    - **调试目的**：通常在调试或开发过程中可能会临时禁用 SSL 验证，但确保在部署到生产环境之前恢复默认的安全设置。
    ### 在请求中禁用 SSL 验证的结论
    虽然可以通过上述方式在 `aiohttp` 中取消 SSL 验证，但始终在应用时保持警惕，确保安全性是你的首要任务。在处理敏感信息或在生产环境中进行通信时，务必保持 SSL 验证的启用状态。
"""


async def fetch(url):
    # 创建一个 SSL 上下文并忽略证书验证
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # 不验证证书

    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=ssl_context) as response:
            return await response.text()


async def main():
    url = "https://cn.bing.com/"
    html = await fetch(url)
    print(html)


if __name__ == '__main__':
    asyncio.run(main())  # 必须用 asyncio.run 启动
