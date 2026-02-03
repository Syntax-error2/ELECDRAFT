# modules/analysis_engine.py
import math

class AnalysisEngine:
    @staticmethod
    def calculate_voltage_drop(current, length, resistance, voltage=230):
        # Formula: Vd = (2 * L * I * R) / 1000
        v_drop = (2 * length * current * resistance) / 1000
        percent_drop = (v_drop / voltage) * 100
        return round(v_drop, 2), round(percent_drop, 2)

    @staticmethod
    def calculate_short_circuit(transformer_kva, impedance_z, voltage=230):
        # Simple Point-to-Point method logic
        full_load_amps = (transformer_kva * 1000) / (voltage * 1.732)
        short_circuit_current = full_load_amps / (impedance_z / 100)
        return round(short_circuit_current, 2)