"""Acceptance tests for US 01 - Building a Concept Database from a CSV.

Each test maps one Given/When/Then acceptance criterion from
``user-stories/us-01-building-concept-database-from-csv.md`` onto the real
``CDBMaker.prepare_csvs`` entry point in ``medcat/cdb_maker.py``.

Fixtures are built as in-memory DataFrames (which ``prepare_csvs`` accepts in
place of CSV paths) so each scenario carries its own distinct, self-describing
clinical concept rather than reusing a shared placeholder (Rule 06).
"""

import logging
import tempfile
import unittest

import pandas as pd

from medcat.cdb import CDB
from medcat.cdb_maker import CDBMaker
from medcat.config import Config


class US01BuildingCDBFromCSVTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        config = Config()
        config.general["spacy_model"] = "en_core_web_md"
        cls.maker = CDBMaker(config)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.maker.destroy_pipe()

    def _build(self, df: pd.DataFrame, full_build: bool = False) -> CDB:
        """Build a fresh CDB from a single DataFrame fixture.

        Args:
            df (pd.DataFrame): The concept rows for this scenario.
            full_build (bool): Whether to populate ``addl_info`` (Default value False).

        Returns:
            CDB: A CDB built solely from ``df``, isolated from other tests.
        """
        self.maker.reset_cdb()
        return self.maker.prepare_csvs([df], full_build=full_build)

    def test_ac1_rows_sharing_one_cui_merge_into_one_concept(self):
        # GIVEN several rows sharing one cui, each supplying a different synonym
        df = pd.DataFrame({
            "cui": ["S-195967001", "S-195967001", "S-195967001"],
            "name": ["Asthma", "Bronchial asthma", "Reactive airway disease"],
        })

        # WHEN prepare_csvs builds the CDB
        cdb = self._build(df)

        # THEN they are merged into a single concept with every name retained
        self.assertEqual(list(cdb.cui2names), ["S-195967001"])
        self.assertEqual(
            cdb.cui2names["S-195967001"],
            {"asthma", "bronchial~asthma", "reactive~airway~disease"},
        )

    def test_ac2_cui_and_name_only_is_enough(self):
        # GIVEN a fixture that supplies only cui and name (no optional columns)
        df = pd.DataFrame({
            "cui": ["S-73211009"],
            "name": ["Diabetes mellitus"],
        })

        # WHEN the CDB is built
        cdb = self._build(df)

        # THEN it succeeds and the optional metadata defaults to empty
        self.assertEqual(cdb.cui2names["S-73211009"], {"diabetes~mellitus"})
        self.assertEqual(cdb.cui2type_ids["S-73211009"], set())

    def test_ac3_names_ontologies_and_type_ids_survive_save_load(self):
        # GIVEN a built CDB carrying names, an ontology tag and type IDs
        df = pd.DataFrame({
            "cui": ["S-84114007"],
            "name": ["Heart failure"],
            "ontologies": ["SNOMED"],
            "name_status": ["P"],
            "type_ids": ["T047|T190"],
            "description": ["Inability of the heart to pump enough blood."],
        })
        cdb = self._build(df, full_build=True)

        # WHEN it is saved with CDB.save and reloaded with CDB.load
        with tempfile.NamedTemporaryFile(suffix=".dat") as f:
            cdb.save(f.name)
            reloaded = CDB.load(f.name)

        # THEN names, ontology tags and type IDs survive the round trip unchanged
        self.assertEqual(reloaded.cui2names, cdb.cui2names)
        self.assertEqual(reloaded.cui2type_ids["S-84114007"], {"T047", "T190"})
        self.assertEqual(
            reloaded.addl_info["cui2ontologies"]["S-84114007"], {"SNOMED"},
        )

    def test_ac4_malformed_rows_are_reported_not_silently_added(self):
        # GIVEN one valid row plus rows missing the required cui / name
        df = pd.DataFrame({
            "cui": ["S-38341003", "", "S-22298006"],
            "name": ["Hypertension", "Orphan without a cui", ""],
        })

        # WHEN the rows are ingested
        with self.assertLogs("medcat.cdb_maker", level=logging.WARNING) as ctx:
            cdb = self._build(df)

        # THEN the malformed rows are reported ...
        self.assertTrue(any("malformed" in msg.lower() for msg in ctx.output))
        # ... and do not corrupt the CDB: only the valid concept is kept
        self.assertEqual(list(cdb.cui2names), ["S-38341003"])
        self.assertNotIn("", cdb.cui2names)
        self.assertNotIn("S-22298006", cdb.cui2names)


if __name__ == "__main__":
    unittest.main()
