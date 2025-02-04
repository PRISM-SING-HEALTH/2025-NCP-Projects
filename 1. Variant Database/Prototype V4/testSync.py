import os 
import unittest 
from unittest.mock import patch, mock_open
from tempfile import TemporaryDirectory
from sync import (
    calculate_file_hash,
    load_metadata,
    save_metadata, 
    check_out_of_sync,
    sync_files,
    update_file_metadata
)

class TestSyncFunctions(unittest.TestCase):
    def test_calculate_file_hash(self):
        with TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_file.txt")
            with open(test_file, "w") as f: 
                f.write("Hello World")

            result = calculate_file_hash(test_file)
            expected_hash = "b10a8db164e0754105b7a99be72e3fe5" # MD5 hash of "Hello World"

            self.assertEqual(result, expected_hash)
    
    def test_load_and_save_metadata(self): 
        metadata = {
            "file1.txt": {"hash": "abcd1234", "version": 1, "last_updated": "2025-01-27T11:42:00Z"}
        }

        with TemporaryDirectory() as temp_dir:
            metadata_file = os.path.join(temp_dir, "metadata.json")

            save_metadata(metadata, metadata_file)

            loaded_metadata = load_metadata(metadata_file)

            self.assertEqual(metadata, loaded_metadata)

    def test_check_out_of_sync(self):
        shared_metadata = {
            "file1.txt": {"hash": "abcd1234", "version": 1, "last_updated": "2025-01-27T11:42:00Z"},
            "file2.txt": {"hash": "efgh5678", "version": 1, "last_updated": "2025-01-27T11:42:00Z"}            
        }
        local_metadata = {
            "file1.txt": {"hash": "abcd1234", "version": 1, "last_updated": "2025-01-27T11:42:00Z"}
        }
        out_of_sync_files = check_out_of_sync(shared_metadata, local_metadata)
        self.assertIn("file2.txt", out_of_sync_files)
        self.assertNotIn("file1.txt", out_of_sync_files)

    def test_sync_files(self):
        with TemporaryDirectory() as shared_dir, TemporaryDirectory() as local_dir: 
            shared_file = os.path.join(shared_dir, "file1.txt")
            with open(shared_file, "w") as f: 
                f.write("Shared content")

            shared_metadata = {
                "file.txt": {"hash": calculate_file_hash(shared_file), "version": 1, "last_updated": "2025-01-27T11:42:00Z"}
            } 
            local_metadata = {}

            local_metadata = sync_files(shared_dir, local_dir, shared_metadata, local_metadata)

            # Verify file exists in local dir
            local_file = os.path.join(local_dir, "file1.txt")
            self.assertTrue(os.path.exists(local_file))

            # Verify content matches 
            with open(local_file, "r") as f: 
                self.assertEquals(f.read(), "Shared content")

            self.assertEqual(local_metadata["file1.txt"]["hash"], shared_metadata["file.txt"]["hash"])

    def test_update_file_metadata(self):
        with TemporaryDirectory() as temp_dir: 
            # Create a file 
            test_file = os.path.join(temp_dir, "file1.txt")
            with open(test_file, "w") as f: 
                f.write("Test content")

            # Create a metadata file
            metadata_file = os.path.join(temp_dir, "metadata.json")
            save_metadata({}, metadata_file)

            # Update metadata
            update_file_metadata(test_file, metadata_file)
            metadata = load_metadata(metadata_file)

            # Verify metadata is updated
            self.assertIn("file1.txt", metadata)
            self.assertEqual(metadata["file1.txt"]["version"], 1)
            self.assertEqual(metadata["file1.txt"]["hash"], calculate_file_hash(test_file))