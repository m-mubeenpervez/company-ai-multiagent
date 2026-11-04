import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts import master_integrity


class ApprovedIntegrityContractTests(unittest.TestCase):
    def test_initial_metadata_requires_versioned_fields(self):
        with self.assertRaises(ValueError):
            master_integrity.validate_initial_integrity_metadata({})
        valid = {"schema": master_integrity.INTEGRITY_METADATA_SCHEMA,
                 "timestamp": "2026-11-04T00:00:00Z", "root": "C:/src",
                 "backup": "C:/backup", "files": 1}
        master_integrity.validate_initial_integrity_metadata(valid)

    def test_inventory_reports_unexpected_non_generated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "keep.txt").write_text("ok")
            (root / "unexpected.txt").write_text("bad")
            (root / ".evaluation_runtime").mkdir()
            (root / ".evaluation_runtime" / "runtime.log").write_text("generated")
            found = master_integrity.inventory_unexpected(root, {"keep.txt"})
            self.assertEqual(found, ["unexpected.txt"])

    def test_inventory_does_not_follow_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target").mkdir()
            (root / "target" / "secret.txt").write_text("secret")
            link = root / "link"
            try:
                link.symlink_to(root / "target", target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaises(RuntimeError):
                master_integrity.inventory_unexpected(root, {"target/secret.txt"})

    def test_main_fails_closed_on_metadata_validation(self):
        with patch.object(Path, "read_text", return_value="{}"), \
             patch.object(master_integrity, "inventory_unexpected") as inventory, \
             patch.object(Path, "write_text") as write:
            with self.assertRaisesRegex(ValueError, "missing required fields"):
                master_integrity.main()
            inventory.assert_not_called()
            write.assert_not_called()

    def test_main_fails_closed_on_inventory_error(self):
        metadata = {"schema": master_integrity.INTEGRITY_METADATA_SCHEMA,
                    "timestamp": "2026-11-04T00:00:00Z", "root": str(master_integrity.ROOT),
                    "backup": ".release_backups/inventory-test", "files": 1}
        manifest = {"keep.txt": {"sha256": "0" * 64}}
        backup = master_integrity.ROOT / ".release_backups/inventory-test"
        with patch.object(Path, "read_text", return_value=json.dumps(metadata)), \
             patch.object(master_integrity, "load_validated_backup", return_value=(backup, backup / "project", manifest)), \
             patch.object(master_integrity, "inventory_unexpected",
                          side_effect=RuntimeError("inventory failure")) as inventory, \
             patch.object(Path, "write_text") as write, \
             patch.object(master_integrity, "digest") as digest:
            with self.assertRaisesRegex(RuntimeError, "^inventory failure$"):
                master_integrity.main()
            inventory.assert_called_once_with(
                master_integrity.ROOT / ".release_backups/inventory-test/project", {"keep.txt"})
            digest.assert_not_called()
            write.assert_not_called()

    def test_validated_backup_rejects_missing_selected_backup_without_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".release_backups/other/project").mkdir(parents=True)
            metadata = {"schema": master_integrity.INTEGRITY_METADATA_SCHEMA,
                        "timestamp": "2026-11-04T00:00:00Z", "root": str(root),
                        "backup": ".release_backups/selected", "files": 1}
            with self.assertRaisesRegex(ValueError, "backup root"):
                master_integrity.load_validated_backup(metadata, root)

    def test_validated_backup_checks_manifest_before_returning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); backup = root / ".release_backups/selected"
            (backup / "project").mkdir(parents=True)
            metadata = {"schema": master_integrity.INTEGRITY_METADATA_SCHEMA,
                        "timestamp": "2026-11-04T00:00:00Z", "root": str(root),
                        "backup": ".release_backups/selected", "files": 1}
            (backup / "manifest.json").write_text(json.dumps({"../escape": {"sha256": "0" * 64}}))
            with self.assertRaisesRegex(ValueError, "traversal"):
                master_integrity.load_validated_backup(metadata, root)

    def test_backup_relocates_with_recorded_root_without_changing_identity(self):
        recorded = master_integrity.ROOT.parent / "previous-project-name"
        relative = Path(".release_backups/master_20261103T231018Z")
        metadata = {"root": str(recorded), "backup": str(recorded / relative)}
        self.assertEqual(master_integrity.resolve_backup_directory(metadata),
                         master_integrity.ROOT / relative)

    def test_backup_resolution_preserves_external_and_relative_paths(self):
        root = master_integrity.ROOT
        external = root.parent / "external-backups" / "selected"
        self.assertEqual(master_integrity.resolve_backup_directory(
            {"root": str(root), "backup": str(external)}), external)
        with tempfile.TemporaryDirectory() as tmp:
            with patch("os.getcwd", return_value=tmp):
                self.assertEqual(master_integrity.resolve_backup_directory(
                    {"root": str(root), "backup": ".release_backups/selected"}),
                    root / ".release_backups/selected")

    def test_missing_selected_backup_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".release_backups/other").mkdir(parents=True)
            selected = master_integrity.resolve_backup_directory(
                {"root": str(root), "backup": ".release_backups/missing"}, root)
            with self.assertRaises(FileNotFoundError):
                (selected / "manifest.json").read_text(encoding="utf-8")

    def test_backup_resolution_rejects_traversal(self):
        with self.assertRaises(ValueError):
            master_integrity.resolve_backup_directory(
                {"root": str(master_integrity.ROOT), "backup": "../other"})


if __name__ == "__main__":
    unittest.main()
