"""Optimized candidate discovery must retain the exact original similarity edges."""
import unittest
from difflib import SequenceMatcher
from hibe.aggregator.collector import dedupe
from hibe.aggregator.models import GrantOpportunity
from hibe.aggregator.textutil import fold


class DedupeSimilarityBoundsTests(unittest.TestCase):
    def test_candidates_equal_exact_reference_at_threshold_and_unicode_boundaries(self):
        titles = [
            'abcdefghij', 'abcdefghiX', 'abcdefghXX', 'abcdeXXXXX',
            'Okul İklim Projesi 2027', 'OKUL IKLIM PROJESI 2027',
            'Öğretmen Eğitimi Avrupa Çağrısı', 'Öğretmen Eğitimi Avrupa Çağrıları',
            'Short', 'A very long unrelated opportunity title with many words',
            'a' * 201 + 'b', 'a' * 201 + 'c', 'b' * 201 + 'a',
        ]
        items = [GrantOpportunity(title, 'source', f'https://official.org/call/{i}',
                  official_call_id=str(i), identity_authority='official') for i, title in enumerate(titles)]
        expected = {item.id: set() for item in items}
        for pos, item in enumerate(items):
            for other in items[pos + 1:]:
                if SequenceMatcher(None, fold(item.title), fold(other.title)).ratio() >= .9:
                    expected[item.id].add(other.id)
                    expected[other.id].add(item.id)
        result = dedupe(items)
        self.assertEqual(len(result), len(items))
        self.assertEqual({item.id: {candidate['id'] for candidate in item.duplicate_candidates} for item in result}, expected)

