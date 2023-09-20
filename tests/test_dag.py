#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from apssdag.dag import AbstractPowerSupplySystemDag


class TestDag:
    def _build_simple_dag() -> AbstractPowerSupplySystemDag:
        pass

    def _build_dag() -> AbstractPowerSupplySystemDag:
        pass

    def test_find_paths_1(self):
        dag = self._build_simple_dag()

        assert dag.find_paths("load_1") == [
            ["power_supply_1", "switch_1", "dc_dc_1", "bus_1", "switch_2", "load_1"],
        ]

    def test_find_paths_2(self):
        dag = self._build_dag()
        assert dag.find_paths("load_1") == [
            ["power_supply_1", "switch_1", "dc_dc_1", "bus_1", "switch_2", "load_1"],
            ["power_supply_2", "switch_1", "dc_dc_1", "bus_1", "switch_2", "load_1"],
        ]
