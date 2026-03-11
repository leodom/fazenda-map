#!/usr/bin/env python3
"""
Improved analysis of Fazenda Santa Fé property coordinates.
This version includes better error handling and verification.
"""

import math
import json
from typing import List, Tuple, Dict

class PropertyAnalyzer:
    def __init__(self, name="Property"):
        self.name = name
        self.segments = []
        self.points = {}
        self.errors = []
        self.warnings = []

    def parse_bearing(self, bearing_str: str) -> float:
        """
        Convert Brazilian quadrant bearing to azimuth (0-360°).
        """
        bearing_str = bearing_str.strip().upper().replace('"', "'")

        # Extract numeric parts and quadrant
        parts = bearing_str.replace('°', ' ').replace("'", ' ').split()

        quadrant = None
        for part in parts:
            if any(q in part for q in ['NE', 'SE', 'SW', 'NW']):
                if 'NE' in part:
                    quadrant = 'NE'
                elif 'SE' in part:
                    quadrant = 'SE'
                elif 'SW' in part:
                    quadrant = 'SW'
                elif 'NW' in part:
                    quadrant = 'NW'
                break

        numeric_parts = []
        for p in parts:
            cleaned = p.replace('NE', '').replace('SE', '').replace('SW', '').replace('NW', '')
            if cleaned and cleaned.replace('.', '').replace(',', '').isdigit():
                numeric_parts.append(float(cleaned))

        if not numeric_parts:
            raise ValueError(f"No numeric parts found in bearing: {bearing_str}")

        degrees = numeric_parts[0]
        minutes = numeric_parts[1] if len(numeric_parts) > 1 else 0.0
        seconds = numeric_parts[2] if len(numeric_parts) > 2 else 0.0

        decimal_degrees = degrees + minutes/60.0 + seconds/3600.0

        # Convert to azimuth (measured clockwise from North)
        if quadrant == 'NE':
            azimuth = decimal_degrees
        elif quadrant == 'SE':
            azimuth = 180 - decimal_degrees
        elif quadrant == 'SW':
            azimuth = 180 + decimal_degrees
        elif quadrant == 'NW':
            azimuth = 360 - decimal_degrees
        else:
            raise ValueError(f"Unknown quadrant in bearing: {bearing_str}")

        return azimuth

    def add_segment(self, from_point: str, to_point: str, distance: float,
                   bearing: str = None, is_curve: bool = False, note: str = ""):
        """Add a segment to the property boundary."""
        segment = {
            'from': from_point,
            'to': to_point,
            'distance': distance,
            'bearing': bearing,
            'is_curve': is_curve,
            'note': note,
            'azimuth': None
        }

        if bearing and not is_curve:
            try:
                segment['azimuth'] = self.parse_bearing(bearing)
            except Exception as e:
                self.errors.append(f"Segment {from_point}->{to_point}: Error parsing '{bearing}': {e}")

        self.segments.append(segment)

    def calculate_coordinates(self, start_x: float = 0, start_y: float = 0):
        """Calculate XY coordinates for all points."""
        self.points = {}
        current_x, current_y = start_x, start_y

        for i, seg in enumerate(self.segments):
            from_point = seg['from']
            to_point = seg['to']
            distance = seg['distance']

            # Set starting point
            if from_point not in self.points:
                if i == 0:
                    self.points[from_point] = (start_x, start_y)
                    current_x, current_y = start_x, start_y
                else:
                    # This point should have been set by a previous segment
                    self.errors.append(f"Segment {i+1}: Starting point '{from_point}' has no coordinates")
                    continue
            else:
                current_x, current_y = self.points[from_point]

            # Calculate endpoint
            if seg['is_curve']:
                # For curves, estimate bearing from next segment or use straight-line approximation
                # Check if the next segment starts from our endpoint
                next_seg = None
                for s in self.segments:
                    if s['from'] == to_point and not s['is_curve'] and s['azimuth'] is not None:
                        next_seg = s
                        break

                if next_seg:
                    # Estimate curve endpoint by assuming it goes roughly in the direction
                    # halfway between our current direction and next direction
                    # For now, use the next segment's reverse bearing
                    reverse_azimuth = (next_seg['azimuth'] + 180) % 360
                    azimuth_rad = math.radians(reverse_azimuth)
                    delta_x = distance * math.sin(azimuth_rad)
                    delta_y = distance * math.cos(azimuth_rad)
                    new_x = current_x + delta_x
                    new_y = current_y + delta_y
                    self.points[to_point] = (new_x, new_y)
                    self.warnings.append(f"Curve {from_point}->{to_point}: position estimated using reverse bearing")
                else:
                    # Last resort: place it relative to start point
                    # Use average of available bearings
                    self.warnings.append(f"Curve {from_point}->{to_point}: position needs manual adjustment")
                continue

            if seg['azimuth'] is None:
                self.errors.append(f"Segment {i+1} ({from_point}->{to_point}): missing valid azimuth")
                continue

            # Calculate delta using azimuth (measured clockwise from North)
            # In surveying: North = Y+, East = X+
            azimuth_rad = math.radians(seg['azimuth'])
            delta_x = distance * math.sin(azimuth_rad)  # East component
            delta_y = distance * math.cos(azimuth_rad)  # North component

            new_x = current_x + delta_x
            new_y = current_y + delta_y

            self.points[to_point] = (new_x, new_y)

        # Handle curve segments by connecting available points
        for seg in self.segments:
            if seg['is_curve']:
                from_pt = seg['from']
                to_pt = seg['to']

                if from_pt in self.points and to_pt not in self.points:
                    # Try to find the next non-curve segment that defines this point
                    for next_seg in self.segments:
                        if next_seg['from'] == to_pt and to_pt not in self.points:
                            # This won't help, skip
                            continue

                # If still not found, estimate
                if from_pt in self.points and to_pt not in self.points:
                    x1, y1 = self.points[from_pt]
                    # Estimate: assume curve goes in a reasonable direction
                    # This is a simplification - real curves would need more data
                    self.points[to_pt] = (x1 + seg['distance'] * 0.7, y1 + seg['distance'] * 0.7)
                    self.warnings.append(f"Curve {from_pt}->{to_pt}: coordinates estimated")

        return self.points

    def check_closure(self) -> Tuple:
        """Check if the polygon closes."""
        if not self.segments:
            return (0, 0, 0)

        first_point = self.segments[0]['from']
        last_point = self.segments[-1]['to']

        if first_point not in self.points or last_point not in self.points:
            return (0, 0, 0)

        x1, y1 = self.points[first_point]
        x2, y2 = self.points[last_point]

        error_x = x2 - x1
        error_y = y2 - y1
        error_distance = math.sqrt(error_x**2 + error_y**2)

        return (error_x, error_y, error_distance)

    def calculate_area_shoelace(self) -> float:
        """Calculate area using the shoelace formula."""
        if len(self.points) < 3:
            return 0

        # Get ordered list of points following the boundary
        coords = []
        visited = set()

        for seg in self.segments:
            if seg['from'] in self.points and seg['from'] not in visited:
                coords.append(self.points[seg['from']])
                visited.add(seg['from'])

        # Shoelace formula
        area = 0
        n = len(coords)
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]

        return abs(area) / 2.0

    def generate_detailed_report(self) -> str:
        """Generate comprehensive analysis report."""
        report = []
        report.append("="*80)
        report.append(f"PROPERTY BOUNDARY ANALYSIS: {self.name}")
        report.append("="*80)
        report.append("")

        # Summary
        report.append(f"Total segments: {len(self.segments)}")
        report.append(f"  Regular segments: {sum(1 for s in self.segments if not s['is_curve'])}")
        report.append(f"  Curve segments: {sum(1 for s in self.segments if s['is_curve'])}")
        report.append(f"Total points calculated: {len(self.points)}")
        report.append("")

        # Errors
        if self.errors:
            report.append("ERRORS:")
            for error in self.errors:
                report.append(f"  ! {error}")
            report.append("")

        # Warnings
        if self.warnings:
            report.append("WARNINGS:")
            for warning in self.warnings:
                report.append(f"  * {warning}")
            report.append("")

        # Closure
        closure = self.check_closure()
        if len(closure) == 3:
            error_x, error_y, error_dist = closure
            report.append("CLOSURE VERIFICATION:")
            report.append(f"  Error in X (East): {error_x:+.3f} m")
            report.append(f"  Error in Y (North): {error_y:+.3f} m")
            report.append(f"  Total closure error: {error_dist:.3f} m")

            total_perimeter = sum(s['distance'] for s in self.segments)
            if total_perimeter > 0 and error_dist > 0.001:
                precision = total_perimeter / error_dist
                report.append(f"  Closure precision: 1:{precision:.0f}")
            elif error_dist < 0.001:
                report.append(f"  Closure precision: PERFECT")

            report.append(f"  Total perimeter: {total_perimeter:,.2f} m")
            report.append("")

        # Area
        calc_area = self.calculate_area_shoelace()
        stated_area = 1568337.90  # From document

        report.append("AREA ANALYSIS:")
        report.append(f"  Calculated area: {calc_area:,.2f} m² ({calc_area/10000:.4f} ha)")
        report.append(f"  Document states: {stated_area:,.2f} m² ({stated_area/10000:.4f} ha)")
        diff = calc_area - stated_area
        diff_pct = (diff / stated_area * 100) if stated_area > 0 else 0
        report.append(f"  Difference: {diff:,.2f} m² ({diff_pct:+.2f}%)")

        if abs(diff_pct) > 5:
            report.append(f"  NOTE: Difference >5% - review curve segments and missing data")
        report.append("")

        # Bounds
        if self.points:
            xs = [p[0] for p in self.points.values()]
            ys = [p[1] for p in self.points.values()]
            report.append("PROPERTY BOUNDS:")
            report.append(f"  X range: {min(xs):.2f} to {max(xs):.2f} m (width: {max(xs)-min(xs):.2f} m)")
            report.append(f"  Y range: {min(ys):.2f} to {max(ys):.2f} m (height: {max(ys)-min(ys):.2f} m)")
            report.append("")

        return "\n".join(report)

    def export_formats(self):
        """Export in multiple formats."""
        # JSON
        data = {
            'property_name': self.name,
            'segments': self.segments,
            'points': {k: {'x': v[0], 'y': v[1]} for k, v in self.points.items()},
            'errors': self.errors,
            'warnings': self.warnings,
            'closure_error': self.check_closure(),
            'calculated_area_m2': self.calculate_area_shoelace()
        }

        with open(f'{self.name.replace(" ", "_")}_analysis.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported: {self.name.replace(' ', '_')}_analysis.json")

        # CSV for GIS
        with open(f'{self.name.replace(" ", "_")}_points.csv', 'w') as f:
            f.write("Point,X_meters,Y_meters\n")
            for seg in self.segments:
                if seg['from'] in self.points:
                    x, y = self.points[seg['from']]
                    f.write(f"{seg['from']},{x:.3f},{y:.3f}\n")
        print(f"Exported: {self.name.replace(' ', '_')}_points.csv")

        # WKT for GIS (Well-Known Text)
        with open(f'{self.name.replace(" ", "_")}_polygon.wkt', 'w') as f:
            coords = []
            for seg in self.segments:
                if seg['from'] in self.points:
                    x, y = self.points[seg['from']]
                    coords.append(f"{x} {y}")
            # Close the polygon
            if self.segments and self.segments[0]['from'] in self.points:
                x, y = self.points[self.segments[0]['from']]
                coords.append(f"{x} {y}")

            wkt = f"POLYGON(({', '.join(coords)}))"
            f.write(wkt)
        print(f"Exported: {self.name.replace(' ', '_')}_polygon.wkt")


def main():
    """Main analysis with corrected data."""
    analyzer = PropertyAnalyzer("Fazenda_Santa_Fe_DESMEMBRADO")

    print("Loading property boundary data from OCR transcription...")
    print("Note: Some segments have OCR issues that have been corrected manually\n")

    # CORRECTED SEGMENT DATA
    # Starting from M-0
    analyzer.add_segment('M-0', 'E-26', 16.20, "94°30'NE")
    analyzer.add_segment('E-26', 'E-27', 104.60, "14°NE")

    # E-27 to E-28: OCR garbled - MISSING DATA
    # For now, going directly to E-30 (assuming E-28, E-29 were intermediate points)
    analyzer.add_segment('E-27', 'E-30', 78.30, "88°45'NE", note="E-28,E-29 missing in OCR")

    analyzer.add_segment('E-30', 'E-31', 21.10, "08°30'NE")
    analyzer.add_segment('E-31', 'E-32', 39.00, "63°27'NE")
    analyzer.add_segment('E-32', 'E-33', 40.90, "42°30'SE")
    analyzer.add_segment('E-33', 'E-34', 71.60, "44°15'NE")
    analyzer.add_segment('E-34', 'E-35', 33.70, "84°00'NE")
    analyzer.add_segment('E-35', 'E-36', 26.30, "32°00'NW")
    analyzer.add_segment('E-36', 'E-37', 55.10, "52°45'NE")

    # E-37 to E-39: E-38 appears to be skipped
    analyzer.add_segment('E-37', 'E-39', 41.30, "83°30'SE", note="E-38 skipped")

    analyzer.add_segment('E-39', 'E-40', 33.40, "37°00'NE")  # Line 66
    analyzer.add_segment('E-40', 'E-41', 55.00, "58°00'NE")  # Line 79

    # CORRECTED: Line 81-82
    analyzer.add_segment('E-41', 'E-42', 25.00, "72°00'SE")

    # CORRECTED: Lines 83-85
    analyzer.add_segment('E-42', 'k-42', 140.00, "49°00'SE", note="OCR: k-42 likely E-42 duplicate")
    analyzer.add_segment('k-42', 'M-13', 345.00, "48°45'SE")

    # Curve along road CMU-009
    analyzer.add_segment('M-13', 'M-14', 285.00, is_curve=True, note="Along road CMU-009")

    analyzer.add_segment('M-14', 'M-15', 950.00, "18°30'NE")
    analyzer.add_segment('M-15', 'M-15A', 327.00, "55°30'SW")
    analyzer.add_segment('M-15A', 'M-15B', 110.00, "24°30'SW")
    analyzer.add_segment('M-15B', 'M-15C', 455.00, "28°00'SE")
    analyzer.add_segment('M-15C', 'M-15D', 240.00, "74°00'SE")
    analyzer.add_segment('M-15D', 'M-15E', 170.00, "48°00'SE")
    analyzer.add_segment('M-15E', 'M-16', 370.00, "08°00'SE")

    analyzer.add_segment('M-16', 'E-43', 90.00, "71°30'NE")
    analyzer.add_segment('E-43', 'E-44', 42.00, "62°15'NW")
    analyzer.add_segment('E-44', 'E-45', 38.00, "61°00'NW")
    analyzer.add_segment('E-45', 'E-46', 77.00, "61°30'NE")
    analyzer.add_segment('E-46', 'E-47', 90.00, "69°30'NW")
    analyzer.add_segment('E-47', 'E-48', 25.00, "76°00'NW")
    analyzer.add_segment('E-48', 'E-49', 220.00, "59°00'NW")
    analyzer.add_segment('E-49', 'M-6', 80.00, "83°17'NW")

    analyzer.add_segment('M-6', 'M-7', 360.00, "167°02'SE")
    analyzer.add_segment('M-7', 'M-8', 110.00, "149°02'SE")
    analyzer.add_segment('M-8', 'M-9', 432.64, "165°20'06\"SE")

    analyzer.add_segment('M-9', 'E-11A', 28.20, "221°10'SW")
    analyzer.add_segment('E-11A', 'E-12', 36.45, "226°33'SW")
    analyzer.add_segment('E-12', 'M-10', 103.78, "238°57'SW")  # Inferred from REMANESCENTE section

    analyzer.add_segment('M-10', 'E-13', 47.63, "145°26'08\"SE")
    analyzer.add_segment('E-13', 'E-14', 86.29, "158°16'SE")
    analyzer.add_segment('E-14', 'E-15', 63.34, "136°21'SE")
    analyzer.add_segment('E-15', 'E-16', 149.83, "157°31'SE")
    analyzer.add_segment('E-16', 'E-17', 146.75, "157°20'SE")
    analyzer.add_segment('E-17', 'E-18', 31.30, "151°36'SE")
    analyzer.add_segment('E-18', 'E-19', 36.93, "245°25'21\"SW")
    analyzer.add_segment('E-19', 'M-11', 58.27, "240°39'SW")

    # Curve along road CMU-007
    analyzer.add_segment('M-11', 'M-1B', 470.00, is_curve=True, note="Along road CMU-007")

    # Final segments to close - bearings estimated
    analyzer.add_segment('M-1B', 'M-1', 100.00, "270°00'NW", note="Bearing estimated")
    analyzer.add_segment('M-1', 'M-0', 430.00, "180°00'SE", note="Bearing estimated to close")

    print("Calculating coordinates...")
    analyzer.calculate_coordinates(start_x=0, start_y=0)

    print("\n" + analyzer.generate_detailed_report())

    print("\nExporting data files...")
    analyzer.export_formats()

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)
    print("\nGenerated files can be imported into:")
    print("  - QGIS (use CSV or WKT file)")
    print("  - Google Earth Pro (convert CSV to KML)")
    print("  - CAD software (use JSON or CSV)")

if __name__ == '__main__':
    main()
