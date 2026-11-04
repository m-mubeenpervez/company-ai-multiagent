import hashlib, json, tempfile, unittest
from pathlib import Path
from scripts.integrity_artifacts import produce_metadata, generate_keypair, sign, verify, component_attestation, bounded_component_attestation, current_component_attestation, verify_current_component_attestation, produce_current_integrity_record, CURRENT_COMPONENT_ROOTS, CURRENT_COMPONENT_FILES, SCHEMA
from evaluations.renderer_contract import validate_current_evidence, validate_output_target

class IntegrityArtifactTests(unittest.TestCase):
    def test_metadata_and_ed25519_tamper_detection(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); backup=root/'backup'; backup.mkdir(); (backup/'a.txt').write_text('a')
            manifest=backup/'manifest.json'; manifest.write_text(json.dumps({'a.txt':{'sha256':'0'*64}}))
            out=root/'meta.json'; data=produce_metadata(manifest,out,str(root),str(backup)); self.assertEqual(data['schema'],SCHEMA); self.assertEqual(data['files'],1)
            priv=root/'private.key'; pub=root/'public.key'; sig=root/'manifest.sig'; generate_keypair(priv,pub); sign(manifest,priv,sig,'local-test'); verify(manifest,pub,sig,'local-test')
            manifest.write_text(manifest.read_text()+' ')
            with self.assertRaises(Exception): verify(manifest,pub,sig,'local-test')
    def test_metadata_rejects_invalid_root(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'m.json'; p.write_text(json.dumps({'a':{'sha256':'0'*64}}))
            with self.assertRaises(ValueError): produce_metadata(p,Path(t)/'o.json',str(Path(t)/'missing'),t)
    def test_component_attestation_excludes_runtime_and_rejects_links(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/'app.py').write_text('x'); (root/'.venv').mkdir(); (root/'.venv'/'x').write_text('cache')
            out=root/'attest.json'; data=component_attestation(str(root),out); self.assertEqual(data['schema'],'companyai.component-attestation.v1'); self.assertEqual(len(data['components']),1)
            (root/'target').mkdir(); (root/'target'/'secret').write_text('s'); link=root/'link'
            try: link.symlink_to(root/'target',target_is_directory=True)
            except (OSError,NotImplementedError): self.skipTest('link unavailable')
            with self.assertRaises(ValueError): component_attestation(str(root),root/'bad.json')

    def test_bounded_attestation_and_renderer_contract(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for d in ('company_system','mcp_server','scripts','evaluations','security','docs'): (root/d).mkdir()
            for f in ('README.md','requirements.txt','requirements-evaluation.txt','requirements-runtime-lock.txt','requirements-evaluation-lock.txt'): (root/f).write_text(f)
            (root/'company_system'/'a.py').write_text('x'); out=root/'attest.json'; data=bounded_component_attestation(str(root),out); self.assertEqual(data['schema'],'companyai.component-attestation.v1')
            source=root/'source.py'; source.write_text('current')
            ev=root/'e.json'; ev.write_text(json.dumps({'results':[], 'provenance': {'source_sha256': {'source.py': hashlib.sha256(source.read_bytes()).hexdigest()}}}))
            receipt=root/'receipt.json'; receipt.write_text(json.dumps({'label':'current','status':'PASS','report':'e.json'}))
            approval={'label':'current','evidence':Path('e.json'),'receipt':Path('receipt.json')}
            validate_current_evidence(ev,root=root,approval=approval)
            with self.assertRaises(ValueError): validate_current_evidence(ev,root=root,approval={})
            with self.assertRaises(PermissionError): validate_output_target(root/'evaluations/results/master_release_decision.json',root=root)
            with self.assertRaises(ValueError): validate_output_target(root/'bad.txt',root=root)

    def test_current_attestation_is_deterministic_and_excludes_outputs_and_signatures(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for d in CURRENT_COMPONENT_ROOTS: (root/d).mkdir()
            for f in CURRENT_COMPONENT_FILES: (root/f).write_text(f)
            (root/'company_system'/'source.py').write_text('source')
            (root/'evaluations'/'results').mkdir(); (root/'evaluations'/'results'/'generated.json').write_text('{}')
            (root/'security'/'artifact.sig').write_text('signature')
            first=root/'current-1.json'; second=root/'current-2.json'
            one=current_component_attestation(str(root),first); two=current_component_attestation(str(root),second)
            self.assertEqual(one,two); self.assertEqual(one['components'],sorted(one['components'],key=lambda row:row['path']))
            paths={row['path'] for row in one['components']}
            self.assertNotIn(str(Path('evaluations/results/generated.json')),paths)
            self.assertNotIn(str(Path('security/artifact.sig')),paths)
            verify_current_component_attestation(str(root),first)

    def test_current_integrity_record_preserves_historical_limitation(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); backup=root/'.release_backups/selected'; backup.mkdir(parents=True)
            historical=root/'historical.json'; historical.write_text(json.dumps({'timestamp':'old'}))
            manifest=backup/'manifest.json'; manifest.write_text('{}')
            att=root/'attestation.json'; att.write_text('{}'); sig=root/'attestation.sig'; sig.write_text('{}')
            output=root/'current.json'; data=produce_current_integrity_record(str(root),output,historical_metadata=historical,backup_manifest=manifest,attestation=att,signature=sig)
            self.assertFalse(data['historical_metadata']['schema_present'])
            self.assertEqual(data['selected_backup']['identity'],'selected')
if __name__=='__main__': unittest.main()
