import unittest
from hibe.service import Service
from hibe.store import MemoryStore
from hibe.demo import seed
from datetime import date

USER={'uid':'user','email':'u@example.org','email_verified':True}

class MembershipTests(unittest.TestCase):
    def setUp(self):
        self.store=MemoryStore();self.service=Service(self.store,'admin')
    def test_free_cannot_export_or_self_upgrade(self):
        for user in ({},dict(USER,email_verified=False)):
            with self.assertRaises(PermissionError):self.service.export_csv(user)
        self.service.preferences(USER,{'themes':[],'subscribed':False,'tier':'pro','membership_status':'active'})
        self.assertEqual(self.service.entitlements(USER)['tier'],'free')
        with self.assertRaises(PermissionError):self.service.export_csv(USER)
    def test_minimal_membership_record_does_not_break_admin_metrics(self):
        self.store.put('users','user',{'tier':'pro','membership_status':'active'})
        values=self.service.metrics({'uid':'admin','email_verified':True})
        self.assertEqual(values['registered'],1)
        self.assertEqual(values['subscribed'],0)
    def test_active_membership_survives_preferences_but_expiry_and_cancel_block(self):
        self.store.put('users','user',{'tier':'pro','membership_status':'active','pro_expires_at':'2999-01-01T00:00:00Z'})
        self.service.preferences(USER,{'themes':[],'subscribed':True})
        self.assertTrue(self.service.entitlements(USER)['features']['csv_export'])
        self.assertFalse(self.service.entitlements(USER)['payments_enabled'])
        self.assertIn('Başlık',self.service.export_csv(USER))
        for change in ({'membership_status':'canceled'},{'pro_expires_at':'2020-01-01T00:00:00Z'},{'pro_expires_at':'2999-01-01'},{'pro_expires_at':'bad'}):
            self.store.put('users','user',dict(tier='pro',membership_status='active',pro_expires_at='2999-01-01T00:00:00Z',**{} )|change)
            with self.assertRaises(PermissionError):self.service.export_csv(USER)
    def test_demo_records_cannot_be_served_by_production_service(self):
        seed(self.store)
        self.assertEqual(self.service.public(),[])
        demo=Service(self.store,'demo-admin',today=lambda:date(2026,10,9),demo=True)
        self.assertTrue(demo.public())
        self.assertTrue(all(c['demo'] for c in demo.public()))
    def test_csv_formula_is_text_and_contains_only_approved_calls(self):
        seed(self.store)
        demo=Service(self.store,'demo-admin',today=lambda:date(2026,10,9),demo=True)
        c=self.store.get('calls','demo-bilim');c['title']='=SUM(1,2)'
        c=demo.save({'uid':'demo-admin','email_verified':True},c);demo.approve({'uid':'demo-admin','email_verified':True},c['id'],c['version'])
        self.store.put('users','user',{'tier':'pro','membership_status':'active'})
        value=demo.export_csv(USER)
        self.assertIn("'=SUM",value);self.assertIn('DEMO',value)
    def test_production_google_token_requires_provider_verification_and_revocation_check(self):
        import sys,types
        from unittest.mock import Mock,patch
        from hibe.server import App
        app=object.__new__(App);app.demo=False
        verify=Mock(return_value=dict(USER,firebase={'sign_in_provider':'google.com'}))
        module=types.ModuleType('firebase_admin');module.auth=types.SimpleNamespace(verify_id_token=verify)
        with patch.dict(sys.modules,{'firebase_admin':module}):
            self.assertEqual(app.user('real-token')['uid'],'user')
            verify.assert_called_once_with('real-token',check_revoked=True)
            for response in (dict(USER,firebase={'sign_in_provider':'password'}),dict(USER,email_verified=False,firebase={'sign_in_provider':'google.com'})):
                verify.return_value=response
                with self.assertRaises(PermissionError):app.user('invalid')
            verify.side_effect=ValueError('revoked')
            with self.assertRaises(PermissionError):app.user('revoked')
    def test_backend_configuration_check_does_not_reveal_values(self):
        import os,sys,types,json
        from unittest.mock import Mock,patch
        from hibe.server import configuration_status,App
        google=types.ModuleType('google');auth=types.ModuleType('google.auth');google.auth=auth
        auth.default=Mock(side_effect=ValueError('credential-secret-must-not-appear'))
        with patch.dict(sys.modules,{'google':google,'google.auth':auth}),patch.dict(os.environ,{},clear=True):
            result=configuration_status()
            self.assertFalse(result['ready']);self.assertIn('ADMIN_UID',result['missing'])
            self.assertNotIn('credential-secret',json.dumps(result))
            with self.assertRaises(ValueError):App(demo=False)
        auth.default=Mock(return_value=(object(),'hibe-radari-tr'))
        values={key:'private-value' for key in ('FIREBASE_PROJECT_ID','FIREBASE_WEB_API_KEY','FIREBASE_AUTH_DOMAIN','FIREBASE_APP_ID','ADMIN_UID')}
        with patch.dict(sys.modules,{'google':google,'google.auth':auth}),patch.dict(os.environ,values,clear=True):
            result=configuration_status();self.assertTrue(result['ready']);self.assertNotIn('private-value',json.dumps(result))
