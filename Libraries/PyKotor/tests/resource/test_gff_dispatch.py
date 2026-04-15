from __future__ import annotations

import pathlib
import sys
import unittest

THIS_SCRIPT_PATH = pathlib.Path(__file__).resolve()
PYKOTOR_PATH = THIS_SCRIPT_PATH.parents[3].joinpath("src")
UTILITY_PATH = THIS_SCRIPT_PATH.parents[5].joinpath("Libraries", "Utility", "src")


def add_sys_path(path: pathlib.Path) -> None:
    working_dir = str(path)
    if working_dir not in sys.path:
        sys.path.append(working_dir)


if PYKOTOR_PATH.joinpath("pykotor").exists():
    add_sys_path(PYKOTOR_PATH)
if UTILITY_PATH.joinpath("utility").exists():
    add_sys_path(UTILITY_PATH)

from pykotor.resource.formats.gff import read_gff
from pykotor.resource.gff_dispatch import (
    SUPPORTED_GFF_RESOURCE_TYPES,
    UNSUPPORTED_GFF_RESOURCE_TYPES,
    get_gff_read_converter,
    get_gff_resource_pipeline,
    is_gff_resource_type,
    reconstruct_gff_as_bytes,
)
from pykotor.resource.type import ResourceType

SUPPORTED_BASE_GFF_TYPES = {
    ResourceType.GFF,
    ResourceType.RES,
    ResourceType.ARE,
    ResourceType.DLG,
    ResourceType.FAC,
    ResourceType.GIT,
    ResourceType.GUI,
    ResourceType.IFO,
    ResourceType.JRL,
    ResourceType.PTH,
    ResourceType.UTC,
    ResourceType.UTD,
    ResourceType.UTE,
    ResourceType.UTI,
    ResourceType.UTM,
    ResourceType.UTP,
    ResourceType.UTS,
    ResourceType.UTT,
    ResourceType.UTW,
}


class TestGFFDispatch(unittest.TestCase):
    def test_supported_base_types_have_complete_pipeline(self) -> None:
        for restype in SUPPORTED_BASE_GFF_TYPES:
            pipeline = get_gff_resource_pipeline(restype)
            self.assertIsNotNone(pipeline, restype)
            assert pipeline is not None
            self.assertIs(get_gff_read_converter(restype), pipeline.read)

    def test_reconstruct_gff_as_bytes_for_supported_type(self) -> None:
        gff = read_gff(
            b"""
            <gff3>
              <struct id="-1">
                <exostring label="Mod_Tag">OnlyTag</exostring>
              </struct>
            </gff3>
            """,
            file_format=ResourceType.GFF_XML,
        )

        rebuilt = reconstruct_gff_as_bytes(gff, ResourceType.IFO)

        self.assertIsNotNone(rebuilt)
        assert rebuilt is not None
        self.assertGreater(len(rebuilt), 0)

    def test_reconstruct_gff_as_bytes_for_generic_gff_type(self) -> None:
        gff = read_gff(
            b"""
            <gff3>
              <struct id="-1">
                <byte label="Value">1</byte>
              </struct>
            </gff3>
            """,
            file_format=ResourceType.GFF_XML,
        )

        rebuilt = reconstruct_gff_as_bytes(gff, ResourceType.GFF)

        self.assertIsNotNone(rebuilt)
        assert rebuilt is not None
        self.assertGreater(len(rebuilt), 0)

    def test_reconstruct_gff_as_bytes_for_unsupported_type(self) -> None:
        gff = read_gff(
            b"""
            <gff3>
              <struct id="-1">
                <byte label="Value">1</byte>
              </struct>
            </gff3>
            """,
            file_format=ResourceType.GFF_XML,
        )

        rebuilt = reconstruct_gff_as_bytes(gff, ResourceType.CWA)

        self.assertIsNone(rebuilt)

    def test_all_gff_resource_types_are_accounted_for(self) -> None:
        all_gff_types = {
            restype
            for restype in ResourceType
            if is_gff_resource_type(restype)
        }

        self.assertEqual(
            SUPPORTED_GFF_RESOURCE_TYPES | UNSUPPORTED_GFF_RESOURCE_TYPES,
            all_gff_types,
        )
        self.assertFalse(SUPPORTED_GFF_RESOURCE_TYPES & UNSUPPORTED_GFF_RESOURCE_TYPES)

    def test_alias_types_resolve_to_supported_pipelines(self) -> None:
        self.assertIsNotNone(get_gff_resource_pipeline(ResourceType.FAC_XML))
        self.assertIsNotNone(get_gff_resource_pipeline(ResourceType.GUI_XML))
        self.assertIsNotNone(get_gff_resource_pipeline(ResourceType.BTD))
        self.assertIsNotNone(get_gff_resource_pipeline(ResourceType.BTI))
        self.assertIsNotNone(get_gff_resource_pipeline(ResourceType.RES_XML))