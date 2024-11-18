import unittest
from visualizer import read_config, generate_mermaid_code

class TestVisualizer(unittest.TestCase):
    def test_read_config(self):
        config = read_config("config.csv")
        self.assertEqual(config["package_name"], "curl")
        self.assertEqual(config["max_depth"], 3)

    def test_generate_mermaid_code(self):
        deps = [("curl", "libcurl"), ("libcurl", "openssl")]
        mermaid_code = generate_mermaid_code(deps)
        expected = "graph TD\n    curl --> libcurl\n    libcurl --> openssl"
        self.assertEqual(mermaid_code.strip(), expected)

if __name__ == "__main__":
    unittest.main()
