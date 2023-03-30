import arcpy
import csv
import re
import json
import pandas as pd
import os
from datetime import date

class Toolbox(object):
    def __init__(self):
        self.label = "Toolbox"
        self.alias = "toolbox"
        self.tools = [Tool]

class Tool(object):
    def __init__(self):
        self.label = "Export Field to CSV"
        self.description = "Exports the contents of the 'display_json' field to a CSV file for features that intersect with an area of interest (AOI)."
        self.canRunInBackground = False

    def getParameterInfo(self):
        aoi_fc = arcpy.Parameter(
            displayName="Area of Interest",
            name="aoi_fc",
            datatype="GPFeatureRecordSetLayer",
            parameterType="Required",
            direction="Input")

        input_fc = arcpy.Parameter(
            displayName="Input Feature Class",
            name="input_fc",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        field_name = arcpy.Parameter(
            displayName="Field Name",
            name="field_name",
            datatype="Field",
            parameterType="Derived",
            direction="Input")
        field_name.parameterDependencies = [input_fc.name]
        field_name.value = "display_json"

        out_name = arcpy.Parameter(
            displayName="Output Name",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        output_param = arcpy.Parameter(
            displayName = "Output parameter",
            name = "output_param",
            datatype = "DEFile",
            parameterType = "Derived",
            direction = "Output")

        species_filter = arcpy.Parameter(
            displayName="Species Filter",
            name="species_filter",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        species_filter.filter.type = "ValueList"
        species_filter.filter.list = ["All Species", "Bird", "Mammal", "Reptile"]

        params = [aoi_fc, input_fc, field_name, out_name, output_param, species_filter]
        return params

    def execute(self, parameters, messages):
        aoi_fc = parameters[0].valueAsText
        input_fc = parameters[1].valueAsText
        field_name = "display_json"
        out_name = parameters[3].valueAsText
        species_filter = parameters[5].valueAsText

        arcpy.env.scratchWorkspace  

        field_values = []
        intersect_fc = arcpy.management.SelectLayerByLocation(input_fc, "INTERSECT", aoi_fc)

        with arcpy.da.SearchCursor(intersect_fc, [field_name]) as cursor:
            for row in cursor:
                field_values.append(row[0])

        unique_animal_info = {}
        unique_animal_counts = {}

        output_csv_path = out_name + ".csv"
        out_csv = os.path.join(arcpy.env.scratchWorkspace, output_csv_path)

        # Iterate through the field_values list
        for value in field_values:
            # Read in the JSON data from the row
            parsed_data = json.loads(value)

            for class_common in ['bird_ids', 'mammal_ids', 'reptile_ids']:
                for taxon in parsed_data.get(class_common, []):
                    taxon_id = taxon.get('taxon_id', None)
                    if taxon_id is not None:
                        unique_animal_info.setdefault(taxon_id, taxon)
                        unique_animal_counts[taxon_id] = unique_animal_counts.get(taxon_id, 0) + 1

        # Print a message to the Geoprocessing Messages tab
        arcpy.AddMessage("Unique animal info count: {}".format(len(unique_animal_counts)))

        num_rows = len(field_values)
        arcpy.AddMessage("Number of rows in field_values: {}".format(num_rows))

        # Calculate the percentage presence for each animal
        percentage_presence = {}
        for animal_id, count in unique_animal_counts.items():
            percentage_presence[animal_id] = (count / num_rows) * 100

        # Export unique_animal_info CSV
        with open(out_csv, 'w', newline='') as f:
            writer = csv.writer(f)

            # Add the disclaimers
            today = date.today().strftime("%d-%m-%Y")
            writer.writerow([f"This data was sourced from DCCEEW's Feral Cat Application on this date: {today}"])
            writer.writerow([])
            writer.writerow(["This data has x, y and z disclaimers and use limitations, please note that data might change over time"])
            writer.writerow([])

            # Write the header row
            writer.writerow(['Species Type', 'Taxon ID', 'Scientific Name', 'Common Name', 'Class Common', 'Conservation Status', 'Cat Susceptibility', 'Cat Susceptibility Score', 'Unique Occurrences', 'Percentage Presence', 'Sprat URL'])

            # Write the data rows
            for animal_id, animal_info in unique_animal_info.items():
                if species_filter == "All Species" or animal_info['class_common'] == species_filter:
                    url = f"http://www.environment.gov.au/cgi-bin/sprat/public/publicspecies.pl?taxon_id={animal_id}"
                    writer.writerow([animal_info['class_common'], animal_id, animal_info['sci_name'], animal_info['com_name'], animal_info['class_common'], animal_info['status'], animal_info['cat_sus'], animal_info['cat_score'], unique_animal_counts[animal_id], f"{percentage_presence[animal_id]:.2f}%", url])
        
        arcpy.SetParameter(4, out_csv)

        return



