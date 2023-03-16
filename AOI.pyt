import arcpy
import csv
import re

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

        output_csv = arcpy.Parameter(
            displayName="Output CSV File",
            name="output_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")
        output_csv.filter.list = ['csv']

        species_filter = arcpy.Parameter(
            displayName="Species Filter",
            name="species_filter",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        species_filter.filter.type = "ValueList"
        species_filter.filter.list = ["All Species", "Bird", "Mammal", "Reptile"]

        params = [aoi_fc, input_fc, field_name, output_csv, species_filter]
        return params

    def execute(self, parameters, messages):
        aoi_fc = parameters[0].valueAsText
        input_fc = parameters[1].valueAsText
        field_name = "display_json"
        output_csv = parameters[3].valueAsText
        species_filter = parameters[4].valueAsText

        field_values = []
        intersect_fc = arcpy.management.SelectLayerByLocation(input_fc, "INTERSECT", aoi_fc)

        with arcpy.da.SearchCursor(intersect_fc, [field_name]) as cursor:
            for row in cursor:
                field_values.append(row[0])

        # Read in the JSON data from field values
        data = [{'display_json': value} for value in field_values]

        # Define regular expressions to match the taxon IDs
        bird_pattern = re.compile(r'"bird_ids":.*?"taxon_id": "(\d+)"')
        mammal_pattern = re.compile(r'"mammal_ids":.*?"taxon_id": "(\d+)"')
        reptile_pattern = re.compile(r'"reptile_ids":.*?"taxon_id": "(\d+)"')

        # Extract the unique bird IDs and associated information
        bird_ids = []
        for record in data:
            display_json = record.get('display_json', '')
            match = bird_pattern.search(display_json)
            if match:
                bird_ids.append(match.group(1))

        unique_bird_ids = set(bird_ids)
        unique_bird_info = {}
        for bird_id in unique_bird_ids:
            unique_bird_info[bird_id] = {'sci_name': '', 'com_name': '', 'class_common': '', 'status': '', 'cat_sus': '', 'cat_score': ''}

        for record in data:
            display_json = record.get('display_json', '')
            for bird_id in unique_bird_ids:
                if f'"taxon_id": "{bird_id}"' in display_json:
                    bird_data = re.search(r'"taxon_id": "{}".*?"sci_name": "(.*?)".*?"com_name": "(.*?)".*?"class_common": "(.*?)".*?"status": "(.*?)".*?"cat_sus": "(.*?)".*?"cat_score": (.*?)(?:,|\}})'.format(bird_id), display_json, re.DOTALL)
                    if bird_data:
                       sci_name, com_name, class_common, status, cat_sus, cat_score = bird_data.groups()
                       unique_bird_info[bird_id] = {'sci_name': sci_name, 'com_name': com_name, 'class_common': class_common, 'status': status, 'cat_sus': cat_sus, 'cat_score': cat_score}

        # Extract the unique mammal IDs and associated information
        mammal_ids = []
        for record in data:
            display_json = record.get('display_json', '')
            match = mammal_pattern.search(display_json)
            if match:
                mammal_ids.append(match.group(1))

        unique_mammal_ids = set(mammal_ids)
        unique_mammal_info = {}
        for mammal_id in unique_mammal_ids:
            unique_mammal_info[mammal_id] = {'sci_name': '', 'com_name': '', 'class_common': '', 'status': '', 'cat_sus': '', 'cat_score': ''}

        for record in data:
            display_json = record.get('display_json', '')
            for mammal_id in unique_mammal_ids:
                if f'"taxon_id": "{mammal_id}"' in display_json:
                    mammal_data = re.search(r'"taxon_id": "{}".*?"sci_name": "(.*?)".*?"com_name": "(.*?)".*?"class_common": "(.*?)".*?"status": "(.*?)".*?"cat_sus": "(.*?)".*?"cat_score": (.*?)(?:,|\}})'.format(mammal_id), display_json, re.DOTALL)
                    if mammal_data:
                        sci_name, com_name, class_common, status, cat_sus, cat_score = mammal_data.groups()
                        unique_mammal_info[mammal_id] = {'sci_name': sci_name, 'com_name': com_name, 'class_common': class_common, 'status': status, 'cat_sus': cat_sus, 'cat_score': cat_score}
            
        # Extract the unique reptile IDs and associated information
        reptile_ids = []
        for record in data:
            display_json = record.get('display_json', '')
            match = reptile_pattern.search(display_json)
            if match:
                reptile_ids.append(match.group(1))

        unique_reptile_ids = set(reptile_ids)
        unique_reptile_info = {}
        for reptile_id in unique_reptile_ids:
            unique_reptile_info[reptile_id] = {'sci_name': '', 'com_name': '', 'class_common': '', 'status': '', 'cat_sus': '', 'cat_score': ''}

        for record in data:
            display_json = record.get('display_json', '')
            for reptile_id in unique_reptile_ids:
                if f'"taxon_id": "{reptile_id}"' in display_json:
                    reptile_data = re.search(r'"taxon_id": "{}".*?"sci_name": "(.*?)".*?"com_name": "(.*?)".*?"class_common": "(.*?)".*?"status": "(.*?)".*?"cat_sus": "(.*?)".*?"cat_score": (.*?)(?:,|\}})'.format(reptile_id), display_json, re.DOTALL)
                    if reptile_data:
                        sci_name, com_name, class_common, status, cat_sus, cat_score = reptile_data.groups()
                        unique_reptile_info[reptile_id] = {'sci_name': sci_name, 'com_name': com_name, 'class_common': class_common, 'status': status, 'cat_sus': cat_sus, 'cat_score': cat_score}

        # Prepare to export a csv
        unique_animals = {
            'Bird': unique_bird_info,
            'Mammal': unique_mammal_info,
            'Reptile': unique_reptile_info
        }

        animal_counts = {
            'Bird': {bird_id: bird_ids.count(bird_id) for bird_id in unique_bird_ids},
            'Mammal': {mammal_id: mammal_ids.count(mammal_id) for mammal_id in unique_mammal_ids},
            'Reptile': {reptile_id: reptile_ids.count(reptile_id) for reptile_id in unique_reptile_ids}
        }

        # Export unique_animals_info CSV
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Type', 'ID', 'Scientific Name', 'Common Name', 'Class Common', 'Status', 'Cat Sus', 'Cat Score', 'Count'])

            for class_common, animal_info_dict in unique_animals.items():
                for animal_id, animal_info in animal_info_dict.items():
                    if species_filter == "All Species" or animal_info['class_common'] == species_filter:
                        writer.writerow([animal_info['class_common'], animal_id, animal_info['sci_name'], animal_info['com_name'], animal_info['class_common'], animal_info['status'], animal_info['cat_sus'], animal_info['cat_score'], animal_counts[class_common][animal_id]])

        return


