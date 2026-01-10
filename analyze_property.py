#!/usr/bin/env python3
"""
Analysis of Fazenda Santa Fé property coordinates from OCR transcription.
This script extracts, processes, and verifies the property boundary data.
"""

import math
import json
from typing import List, Tuple, Dict

class PropertyAnalyzer:
    def __init__(self):
        self.segments = []
        self.points = {}
        self.errors = []

    def parse_bearing(self, bearing_str: str) -> float:
        """
        Convert Brazilian quadrant bearing to azimuth (0-360°).
        Brazilian format: [angle][quadrant]
        Examples: 94°30'NE, 14°NE, 48°45'SE

        Quadrant conversions:
        - NE: azimuth = angle
        - SE: azimuth = 180 - angle
        - SW: azimuth = 180 + angle
        - NW: azimuth = 360 - angle
        """
        bearing_str = bearing_str.strip().upper()

        # Extract degrees, minutes, seconds
        parts = bearing_str.replace('°', ' ').replace("'", ' ').replace('"', ' ').split()

        # Find quadrant
        quadrant = None
        for part in parts:
            if 'NE' in part or 'SE' in part or 'SW' in part or 'NW' in part:
                quadrant = part.replace('NE', '').replace('SE', '').replace('SW', '').replace('NW', '')
                if 'NE' in part:
                    quadrant = 'NE'
                elif 'SE' in part:
                    quadrant = 'SE'
                elif 'SW' in part:
                    quadrant = 'SW'
                elif 'NW' in part:
                    quadrant = 'NW'
                break

        # Extract numeric parts
        numeric_parts = [p for p in parts if p.replace('.', '').replace(',', '').isdigit()]

        if not numeric_parts:
            raise ValueError(f"No numeric parts found in bearing: {bearing_str}")

        degrees = float(numeric_parts[0])
        minutes = float(numeric_parts[1]) if len(numeric_parts) > 1 else 0.0
        seconds = float(numeric_parts[2]) if len(numeric_parts) > 2 else 0.0

        # Convert to decimal degrees
        decimal_degrees = degrees + minutes/60.0 + seconds/3600.0

        # Convert to azimuth based on quadrant
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
                   bearing: str = None, is_curve: bool = False):
        """Add a segment to the property boundary."""
        segment = {
            'from': from_point,
            'to': to_point,
            'distance': distance,
            'bearing': bearing,
            'is_curve': is_curve
        }

        if bearing and not is_curve:
            try:
                segment['azimuth'] = self.parse_bearing(bearing)
            except Exception as e:
                self.errors.append(f"Error parsing bearing '{bearing}': {e}")
                segment['azimuth'] = None

        self.segments.append(segment)

    def calculate_coordinates(self, start_x: float = 0, start_y: float = 0):
        """Calculate XY coordinates for all points starting from origin."""
        self.points = {self.segments[0]['from']: (start_x, start_y)}

        current_x, current_y = start_x, start_y

        for i, seg in enumerate(self.segments):
            from_point = seg['from']
            to_point = seg['to']
            distance = seg['distance']

            if seg['is_curve']:
                # For curves, we'll approximate with a straight line for now
                # In reality, we'd need more info about the curve
                if to_point in self.points:
                    current_x, current_y = self.points[to_point]
                else:
                    self.errors.append(f"Curve segment {from_point}->{to_point}: coordinates not determined")
                continue

            if seg['azimuth'] is None:
                self.errors.append(f"Segment {i+1} ({from_point}->{to_point}): missing azimuth")
                continue

            # Calculate delta x and delta y
            azimuth_rad = math.radians(seg['azimuth'])
            delta_x = distance * math.sin(azimuth_rad)
            delta_y = distance * math.cos(azimuth_rad)

            # Update current position
            if from_point not in self.points:
                self.points[from_point] = (current_x, current_y)
            else:
                current_x, current_y = self.points[from_point]

            current_x += delta_x
            current_y += delta_y

            self.points[to_point] = (current_x, current_y)

        return self.points

    def check_closure(self) -> Tuple[float, float]:
        """Check if the polygon closes (first and last points match)."""
        if not self.segments:
            return (0, 0)

        first_point = self.segments[0]['from']
        last_point = self.segments[-1]['to']

        if first_point not in self.points or last_point not in self.points:
            self.errors.append("Cannot check closure: missing start or end point")
            return (0, 0)

        x1, y1 = self.points[first_point]
        x2, y2 = self.points[last_point]

        error_x = x2 - x1
        error_y = y2 - y1
        error_distance = math.sqrt(error_x**2 + error_y**2)

        return (error_x, error_y, error_distance)

    def calculate_area(self) -> float:
        """Calculate area using the shoelace formula."""
        if len(self.points) < 3:
            return 0

        # Get ordered list of points
        ordered_points = []
        for seg in self.segments:
            if seg['from'] in self.points and seg['from'] not in [p[0] for p in ordered_points]:
                ordered_points.append((seg['from'], self.points[seg['from']]))

        if not ordered_points:
            return 0

        # Shoelace formula
        area = 0
        for i in range(len(ordered_points)):
            j = (i + 1) % len(ordered_points)
            x1, y1 = ordered_points[i][1]
            x2, y2 = ordered_points[j][1]
            area += x1 * y2
            area -= x2 * y1

        return abs(area) / 2.0

    def export_for_visualization(self, filename: str = 'property_plot_data.txt'):
        """Export coordinates in a format suitable for visualization tools."""
        if not self.points:
            print("No points to export")
            return

        with open(filename, 'w') as f:
            f.write("# Property Boundary Coordinates\n")
            f.write("# Format: Point X Y\n")
            f.write("# Can be imported into QGIS, Google Earth, or other GIS software\n\n")

            # Extract coordinates in order
            for seg in self.segments:
                if seg['from'] in self.points:
                    x, y = self.points[seg['from']]
                    f.write(f"{seg['from']}\t{x:.2f}\t{y:.2f}\n")

            # Add last point
            if self.segments:
                last_point = self.segments[-1]['to']
                if last_point in self.points:
                    x, y = self.points[last_point]
                    f.write(f"{last_point}\t{x:.2f}\t{y:.2f}\n")

        print(f"Visualization data saved to {filename}")

    def create_ascii_plot(self):
        """Create a simple ASCII visualization of the property."""
        if not self.points:
            return

        # Get all coordinates
        coords = list(self.points.values())
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]

        # Find bounds
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = max_x - min_x
        height = max_y - min_y

        print("\n" + "="*60)
        print("ASCII VISUALIZATION (approximate)")
        print("="*60)
        print(f"X range: {min_x:.1f} to {max_x:.1f} meters (width: {width:.1f}m)")
        print(f"Y range: {min_y:.1f} to {max_y:.1f} meters (height: {height:.1f}m)")
        print("Note: Use the exported CSV/JSON files for accurate visualization in GIS software")
        print("="*60 + "\n")

    def generate_report(self) -> str:
        """Generate a detailed analysis report."""
        report = []
        report.append("="*80)
        report.append("PROPERTY BOUNDARY ANALYSIS REPORT")
        report.append("Fazenda Santa Fé - DESMEMBRADO")
        report.append("="*80)
        report.append("")

        report.append(f"Total segments: {len(self.segments)}")
        report.append(f"Total points: {len(self.points)}")
        report.append("")

        if self.errors:
            report.append("ERRORS AND WARNINGS:")
            for error in self.errors:
                report.append(f"  - {error}")
            report.append("")

        # Closure check
        closure = self.check_closure()
        if len(closure) == 3:
            error_x, error_y, error_dist = closure
            report.append("CLOSURE CHECK:")
            report.append(f"  Error in X: {error_x:.2f} m")
            report.append(f"  Error in Y: {error_y:.2f} m")
            report.append(f"  Total error: {error_dist:.2f} m")

            total_perimeter = sum(seg['distance'] for seg in self.segments if not seg['is_curve'])
            if total_perimeter > 0 and error_dist > 0:
                closure_precision = error_dist / total_perimeter
                report.append(f"  Closure precision: 1:{1/closure_precision:.0f}")
            elif error_dist == 0:
                report.append(f"  Closure precision: Perfect (no error)")
            report.append("")

        # Area calculation
        calculated_area = self.calculate_area()
        stated_area = 1568337.90  # m² from document

        report.append("AREA CALCULATION:")
        report.append(f"  Calculated area: {calculated_area:,.2f} m²")
        report.append(f"  Stated area: {stated_area:,.2f} m²")
        report.append(f"  Difference: {calculated_area - stated_area:,.2f} m²")
        report.append(f"  Difference %: {((calculated_area - stated_area) / stated_area * 100):.2f}%")
        report.append("")

        # Perimeter
        total_perimeter = sum(seg['distance'] for seg in self.segments)
        report.append(f"Total perimeter: {total_perimeter:,.2f} m")
        report.append("")

        return "\n".join(report)


def main():
    """Main analysis function."""
    analyzer = PropertyAnalyzer()

    # DESMEMBRADO - Extracted from the document
    # Note: Some segments have missing data due to OCR issues

    print("Loading property data...")

    # Segment data extracted from document
    analyzer.add_segment('M-0', 'E-26', 16.20, "94°30'NE")
    analyzer.add_segment('E-26', 'E-27', 104.60, "14°NE")
    # E-27 to E-28: distance and bearing missing in OCR - SKIP for now
    # analyzer.add_segment('E-27', 'E-28', ???, "???")
    analyzer.add_segment('E-27', 'E-30', 78.30, "88°45'NE")  # Assuming E-28 was skipped
    analyzer.add_segment('E-30', 'E-31', 21.10, "08°30'NE")
    analyzer.add_segment('E-31', 'E-32', 39.00, "63°27'NE")
    analyzer.add_segment('E-32', 'E-33', 40.90, "42°30'SE")
    analyzer.add_segment('E-33', 'E-34', 71.60, "44°15'NE")
    analyzer.add_segment('E-34', 'E-35', 33.70, "84°00'NE")
    analyzer.add_segment('E-35', 'E-36', 26.30, "32°00'NW")
    analyzer.add_segment('E-36', 'E-37', 55.10, "52°45'NE")
    analyzer.add_segment('E-37', 'E-39', 41.30, "83°30'SE")  # Note: E-38 missing
    analyzer.add_segment('E-39', 'E-40', 33.40, "37°00'NE")
    analyzer.add_segment('E-40', 'E-41', 55.00, "58°00'NE")
    analyzer.add_segment('E-41', 'E-42', 25.00, "72°00'SE")
    analyzer.add_segment('E-42', 'M-13', 140.00, "49°00'SE")
    analyzer.add_segment('M-13', 'M-13', 345.00, "48°45'SE")  # Typo? Should be M-13 to next point

    # Curve segment
    analyzer.add_segment('M-13', 'M-14', 285.00, is_curve=True)

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
    analyzer.add_segment('E-12', 'M-10', 103.78, "238°57'SW")  # Inferred from REMANESCENTE
    analyzer.add_segment('M-10', 'E-13', 47.63, "145°26'08\"SE")
    analyzer.add_segment('E-13', 'E-14', 86.29, "158°16'SE")
    analyzer.add_segment('E-14', 'E-15', 63.34, "136°21'SE")
    analyzer.add_segment('E-15', 'E-16', 149.83, "157°31'SE")
    analyzer.add_segment('E-16', 'E-17', 146.75, "157°20'SE")
    analyzer.add_segment('E-17', 'E-18', 31.30, "151°36'SE")
    analyzer.add_segment('E-18', 'E-19', 36.93, "245°25'21\"SW")
    analyzer.add_segment('E-19', 'M-11', 58.27, "240°39'SW")

    # Curve segment
    analyzer.add_segment('M-11', 'M-1B', 470.00, is_curve=True)

    # Missing bearings for final segments
    analyzer.add_segment('M-1B', 'M-1', 100.00, "270°NW")  # Estimated
    analyzer.add_segment('M-1', 'M-0', 430.00, "180°SE")  # Estimated to close

    print("Calculating coordinates...")
    analyzer.calculate_coordinates()

    print("\n" + analyzer.generate_report())

    print("\nGenerating visualization data...")
    analyzer.export_for_visualization()

    # Export coordinates to JSON
    coords_data = {
        'segments': analyzer.segments,
        'points': {k: {'x': v[0], 'y': v[1]} for k, v in analyzer.points.items()},
        'errors': analyzer.errors
    }

    with open('property_coordinates.json', 'w') as f:
        json.dump(coords_data, f, indent=2)
    print("Coordinates exported to property_coordinates.json")

    # Export to CSV for GIS software
    with open('property_points.csv', 'w') as f:
        f.write("Point,X,Y\n")
        for point_name, (x, y) in sorted(analyzer.points.items()):
            f.write(f"{point_name},{x},{y}\n")
    print("Points exported to property_points.csv")

    print("\nAnalysis complete!")

if __name__ == '__main__':
    main()
