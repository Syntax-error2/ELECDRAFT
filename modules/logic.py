import math


class PECCalculator:
    @staticmethod
    def calculate_load(va, voltage=230, length=30, is_continuous=False):
        """
        Comprehensive PEC-compliant branch circuit calculation.
        Args:
            va: Volt-Ampere load
            voltage: System voltage (default 230V)
            length: Distance in meters for Voltage Drop (default 30m)
            is_continuous: Whether the load runs for 3+ hours (e.g., lighting)
        Returns: (Amps, Breaker, Wire, Voltage Drop %)
        """
        # 1. Apply Continuous Load Factor (PEC Requirement: 125%)
        # This ensures the breaker and wire handle heat over long periods.
        calculation_va = va * 1.25 if is_continuous else va

        # 2. Base Amperage
        amps = calculation_va / voltage

        # 3. Breaker Selection
        # PEC requires branch circuit protection to be at least 125% of continuous load
        req_ampacity = amps * 1.25 if not is_continuous else amps

        # Standard Philippine Breaker Ratings (Ampere Trip - AT)
        standard_breakers = [15, 20, 30, 40, 50, 60, 70, 80, 100, 125]
        breaker = next((b for b in standard_breakers if b >= req_ampacity), 20)

        # 4. Wire Sizing & Resistance (Based on PEC Table 3.10.1.16)
        # Assuming Copper THHN/THWN-2 in Raceway (75°C insulation column)
        if breaker <= 20:
            wire = "3.5mm² THHN"
            resistance = 5.2  # Ohms/km (Approximate for 3.5mm²)
        elif breaker <= 30:
            wire = "5.5mm² THHN"
            resistance = 3.3  # Ohms/km (Approximate for 5.5mm²)
        elif breaker <= 50:
            wire = "8.0mm² THHN"
            resistance = 2.1  # Ohms/km (Approximate for 8.0mm²)
        elif breaker <= 60:
            wire = "14.0mm² THHN"
            resistance = 1.3  # Ohms/km (Approximate for 14.0mm²)
        else:
            wire = "22.0mm² THHN"
            resistance = 0.85  # Ohms/km (Approximate for 22.0mm²)

        # 5. Voltage Drop Calculation (PEC Recommendation: Max 3% for branch circuits)
        # Formula: VD = (2 * L * I * R) / 1000 for single phase
        v_drop = (2 * length * (va / voltage) * resistance) / 1000
        vd_percentage = (v_drop / voltage) * 100

        return round(amps, 2), breaker, wire, round(vd_percentage, 2)

    @staticmethod
    def calculate_short_circuit(kva_trans=50, z_percent=2.0, voltage=230):
        """
        Calculates Available Symmetrical Fault Current (Isc).
        Used to determine the Interrupting Capacity (KAIC) of breakers.
        """
        # Calculate Transformer Full Load Amps (FLA)
        fla = (kva_trans * 1000) / voltage

        # Symmetrical Fault Current Isc = FLA / Z_percent (expressed as decimal)
        i_sc = fla / (z_percent / 100)

        return round(i_sc / 1000, 2)  # Returns result in kA