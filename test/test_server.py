"""Integrate test for jarvis project
"""

import unittest
from server.server import JarvisServer


class TestJarvisServerMethod(unittest.TestCase):
    """Integrate test for jarvis server"""

    def test_memo_routine(self):
        """Test create, update, read, delete memo"""

        name = "Untitled"
        content = "There is no content"

        JarvisServer.create_memo(name=name, content=content)

        self.assertEqual(JarvisServer.count_memo(), 1)

        memo = JarvisServer.latest_memo()

        self.assertEqual(memo.name, name)
        self.assertEqual(memo.content, content)


if __name__ == "__main__":
    unittest.main()
