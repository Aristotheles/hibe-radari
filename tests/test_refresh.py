import unittest
from unittest.mock import patch
from hibe.refresh import refresh
from hibe.store import MemoryStore


class RefreshTests(unittest.TestCase):
    def test_only_permitted_sources_and_review_candidates_are_persisted(self):
        config = {'sources': [
            {'id': 'allowed', 'access_policy': {'terms_status': 'allowed'}},
            {'id': 'unknown', 'access_policy': {'terms_status': 'unreviewed'}},
            {'id': 'restricted', 'access_policy': {'terms_status': 'permission_required'}}]}
        report = {'run_status': 'partial', 'sources': [{'id': 'allowed', 'health': 'success'}],
                  'counts': {}, 'accepted': [], 'review': [{'id': 'candidate'}],
                  'watch': [], 'general': [{'id': 'news'}], 'rejected': [{'id': 'noise'}]}
        with patch('hibe.refresh.load_config', return_value=config), \
             patch('hibe.refresh.due_sources', return_value=['allowed']), \
             patch('hibe.refresh.run', return_value=report) as run, \
             patch('hibe.refresh.write_report') as write, \
             patch('hibe.refresh.persist_report', return_value=1) as persist:
            result = refresh(MemoryStore())
        self.assertEqual([s['id'] for s in run.call_args.kwargs['config']['sources']], ['allowed'])
        self.assertEqual(run.call_args.kwargs['only'], ['allowed'])
        passed = persist.call_args.args[0]
        self.assertEqual(passed['review'], [{'id': 'candidate'}])
        self.assertEqual(passed['general'], [])
        self.assertEqual(passed['rejected'], [])
        self.assertEqual(write.call_args.args[1].name, 'refresh-attempt.json')
        self.assertEqual(result['changed'], 1)
        self.assertEqual(result['unhealthy'], [])

    def test_not_due_does_not_fetch_or_modify_store(self):
        with patch('hibe.refresh.load_config', return_value={'sources': []}), \
             patch('hibe.refresh.due_sources', return_value=[]), \
             patch('hibe.refresh.run') as run, patch('hibe.refresh.persist_report') as persist:
            self.assertEqual(refresh(MemoryStore())['status'], 'not_due')
        run.assert_not_called()
        persist.assert_not_called()
