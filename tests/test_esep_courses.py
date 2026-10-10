import unittest,json
from pathlib import Path
from datetime import date
from unittest.mock import Mock
from hibe.aggregator.html_cards import collect_list
class EsepTests(unittest.TestCase):
 def test_observed_links_preserve_unique_courses_and_reject_navigation(self):
  config=json.loads(Path('config/aggregator.json').read_text('utf-8'))
  source=next(x for x in config['sources'] if x['id']=='esep-courses')
  fetcher=Mock();fetcher.get_text.return_value=Path('tests/fixtures/esep-courses-list.html').read_text('utf-8')
  items=collect_list(source,fetcher,date(2026,10,10))
  self.assertGreaterEqual(len(items),8)
  self.assertEqual(len(items),len({i.source_url for i in items}))
  self.assertTrue(all('/en/learn/courses/' in i.source_url for i in items))
  self.assertTrue(all(i.deadline is None for i in items))
 def test_unrelated_page_is_empty_not_fabricated_course(self):
  source={'url':'https://example.org/','link_pattern':'^/en/learn/courses/[^/]+$'}
  fetcher=Mock();fetcher.get_text.return_value='<a href="/news">News with a long title</a>'
  self.assertEqual(collect_list(source,fetcher,date.today()),[])
