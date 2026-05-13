import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestFileService(unittest.TestCase):
    def test_read_root(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("project", response.json())

    def test_read_dir_invalid(self):
        response = client.get("/api/read-dir?path=/non/existent/path")
        self.assertEqual(response.status_code, 200) # We return 200 with error msg
        self.assertEqual(response.json()["code"], 400)

if __name__ == "__main__":
    unittest.main()
