import os
import unittest
from unittest.mock import patch
from hibe.cloud_refresh import main
from hibe.store import MemoryStore


class CloudRefreshTests(unittest.TestCase):
    def test_busy_collect_only_does_not_modify_source_or_submit_again(self):
        from hibe.job_lease import processing_lease
        store=MemoryStore()
        with processing_lease(store,'ai_batch_result_processing'), \
             patch.dict(os.environ,{'FIREBASE_PROJECT_ID':'test','AI_BATCH_COLLECT_ONLY':'true','AI_REVIEW_ENABLED':'true'}), \
             patch('firebase_admin.initialize_app'),patch('hibe.cloud_refresh.FirestoreStore',return_value=store), \
             patch('hibe.cloud_refresh.refresh') as scan,patch('hibe.batch_pipeline.finish_batches') as finish, \
             patch('hibe.batch_pipeline.submit_candidates') as submit,patch('builtins.print'):
            self.assertEqual(main(),0)
        scan.assert_not_called();finish.assert_not_called();submit.assert_not_called()
        self.assertEqual(store.get('automation_runs','batch_collection_latest')['status'],'processing_elsewhere')
    def execute(self, result=None, error=None):
        store = MemoryStore()
        with patch.dict(os.environ, {'FIREBASE_PROJECT_ID': 'test-project'}), \
             patch('firebase_admin.initialize_app') as initialize, \
             patch('hibe.cloud_refresh.FirestoreStore', return_value=store), \
             patch('hibe.cloud_refresh.refresh', return_value=result, side_effect=error), \
             patch('builtins.print') as output:
            code = main()
        initialize.assert_called_once_with(options={'projectId': 'test-project'})
        return code, store.get('automation_runs', 'source_refresh_latest'), output

    def test_uses_service_identity_without_admin_or_web_configuration(self):
        code, receipt, _ = self.execute({'status': 'not_due', 'sources': 0, 'changed': 0})
        self.assertEqual(code, 0)
        self.assertEqual(receipt['status'], 'not_due')
        self.assertIn('finished_at', receipt)

    def test_source_failure_sets_nonzero_exit(self):
        code, _, _ = self.execute({'status': 'partial', 'unhealthy': ['source']})
        self.assertEqual(code, 1)

    def test_exception_does_not_expose_message_and_records_failure(self):
        code, receipt, output = self.execute(error=RuntimeError('secret-credential'))
        self.assertEqual(code, 1)
        self.assertEqual(receipt['error_kind'], 'RuntimeError')
        self.assertNotIn('secret-credential', str(output.call_args))

    def test_missing_project_does_not_initialize(self):
        with patch.dict(os.environ, {}, clear=True), patch('firebase_admin.initialize_app') as initialize:
            with self.assertRaises(ValueError):
                main()
        initialize.assert_not_called()

    def test_collect_only_never_scans_or_submits(self):
        store=MemoryStore()
        with patch.dict(os.environ,{'FIREBASE_PROJECT_ID':'test','AI_BATCH_COLLECT_ONLY':'true','AI_REVIEW_ENABLED':'true'}), \
             patch('firebase_admin.initialize_app'),patch('hibe.cloud_refresh.FirestoreStore',return_value=store), \
             patch('hibe.cloud_refresh.refresh') as scan,patch('hibe.batch_pipeline.finish_batches',return_value={'pending':0}), \
             patch('hibe.batch_pipeline.submit_candidates') as submit,patch('builtins.print'):
            self.assertEqual(main(),0)
        scan.assert_not_called();submit.assert_not_called()
        self.assertIsNone(store.get('automation_runs','source_refresh_latest'))
        self.assertEqual(store.get('automation_runs','batch_collection_latest')['status'],'batch_collection_only')
