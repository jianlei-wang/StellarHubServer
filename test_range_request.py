"""
测试 Range 请求是否正常工作的脚本
"""
import urllib.request
import json

# 测试文件路径
test_file = r"D:\nginx-1.26.3\html\tif\test_cog.tif"
base_url = "http://localhost:10086"

def test_request(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as response:
        return {
            'status': response.status,
            'headers': dict(response.headers),
            'length': len(response.read())
        }

# 测试 1: 不带 Range 头
print("=" * 50)
print("测试 1: 不带 Range 头（应该返回 200）")
print("=" * 50)
result1 = test_request(f"{base_url}/api/file?path={test_file}")
print(f"状态码: {result1['status']}")
print(f"Accept-Ranges: {result1['headers'].get('Accept-Ranges')}")
print(f"Content-Length: {result1['headers'].get('Content-Length')}")
print()

# 测试 2: 带 Range 头（请求前 1KB）
print("=" * 50)
print("测试 2: Range 请求 bytes=0-1023（应该返回 206）")
print("=" * 50)
result2 = test_request(
    f"{base_url}/api/file?path={test_file}",
    headers={"Range": "bytes=0-1023"}
)
print(f"状态码: {result2['status']}")
print(f"Content-Range: {result2['headers'].get('Content-Range')}")
print(f"Accept-Ranges: {result2['headers'].get('Accept-Ranges')}")
print(f"实际下载数据大小: {result2['length']} bytes")
print()

# 测试 3: 带 Range 头（请求中间部分）
print("=" * 50)
print("测试 3: Range 请求 bytes=1000000-1001023（应该返回 206）")
print("=" * 50)
result3 = test_request(
    f"{base_url}/api/file?path={test_file}",
    headers={"Range": "bytes=1000000-1001023"}
)
print(f"状态码: {result3['status']}")
print(f"Content-Range: {result3['headers'].get('Content-Range')}")
print(f"Accept-Ranges: {result3['headers'].get('Accept-Ranges')}")
print(f"实际下载数据大小: {result3['length']} bytes")
print()

print("✅ 测试完成！如果测试 2 和 3 的状态码都是 206，说明 Range 请求支持正常")
