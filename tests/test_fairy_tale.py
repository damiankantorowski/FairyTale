import unittest
import asyncio
from fairy_tale.fairy_tale import FairyTale


class TestFairyTale(unittest.TestCase):
    topics = ["test"]
    def test_init(self):
        fairy_tale = FairyTale(None, *self.topics)
        self.assertIsNotNone(fairy_tale)
        self.assertEqual(fairy_tale.topics, list(self.topics))
    def test_init_no_topics(self):
        with self.assertRaises(ValueError):
            fairy_tale = FairyTale(None)
    def test_topics_setter(self):
        fairy_tale = FairyTale(None, self.topics[0])
        fairy_tale.topics = self.topics
        self.assertListEqual(fairy_tale.topics, self.topics)
    def test_topics_setter_no_topics(self):
        fairy_tale = FairyTale(None, *self.topics)
        with self.assertRaises(ValueError):
            fairy_tale.topics = []
 
class TestFairyTaleAsync(unittest.IsolatedAsyncioTestCase):
    topics = ["test"]
    async def test_fairy_tale_async(self):
        fairy_tale = FairyTale(None, *self.topics)
        await fairy_tale.create_assistant("test", "test", "gpt-3.5-turbo-1106")
        self.assertIsNotNone(fairy_tale.assistant)
        await fairy_tale.write_fairy_tales("test", "test")
        self.assertGreater(len(fairy_tale.responses), 0)
        self.assertIsInstance(fairy_tale.responses[0][0], str)
        await fairy_tale.delete_assistant()
        self.assertIsNone(fairy_tale.assistant)
                     

if __name__ == '__main__':
    unittest.main()
