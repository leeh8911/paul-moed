"""Integrate test for jarvis project
"""

import unittest
from server.server import JarvisServer


class TestJarvisServerMethod(unittest.TestCase):
    """Jarvis server의 메서드에 대한 통합 테스트"""

    def test_memo_routine(self):
        """새로운 메모를 추가, 읽기, 수정, 삭제를 수행한다."""

        name = "Untitled"
        content = "There is no content"

        # 새로운 메모를 추가
        JarvisServer.create_memo(name=name, content=content)

        self.assertEqual(JarvisServer.count_memo(), 1)

        memo = JarvisServer.latest_memo()

        self.assertEqual(memo.name, name)
        self.assertEqual(memo.content, content)

        new_name = "Untitled 2"
        new_content = "There is some content"

        # 메모 수정
        JarvisServer.update_memo(memo, name=new_name, content=new_content)

        self.assertEqual(JarvisServer.count_memo(), 1)

        memo = JarvisServer.latest_memo()

        self.assertEqual(memo.name, new_name)
        self.assertEqual(memo.content, new_content)

        # 메모 삭제
        JarvisServer.delete_memo(memo)

        self.assertEqual(JarvisServer.count_memo(), 0)


if __name__ == "__main__":

    unittest.main()
