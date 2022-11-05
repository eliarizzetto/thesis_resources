# This file contains the base structure wherein to call the validation functions for CITS-CSV.

from helper_functions import content
from validation_functions import wellformedness_id_field, wellformedness_single_id, wellformedness_date
from create_report import create_error_dict
from check_output.check_validation_output import check_validation_output
import re
from pprint import pprint
import yaml
from csv import DictReader
from helper_functions import group_ids


csv_doc = 'C:/Users/media/Desktop/thesis23/thesis_resources/validation_process/validation/test_files/sample_cits.csv'

with open(csv_doc, 'r', encoding='utf-8') as f:
    data_dict = DictReader(f)

    error_final_report = []

    messages = yaml.full_load(open('messages.yaml', 'r', encoding='utf-8'))

    for row_idx, row in enumerate(data_dict):

        for field, value in row.items():
            if content(value):
                if field == 'citing_id' or field == 'cited_id':
                    items = re.split('\s', value)

                    for item_idx, item in enumerate(items):

                        if item == '':
                            message = messages['m1']
                            table = {row_idx: {field: [item_idx]}}
                            error_final_report.append(
                                create_error_dict(validation_level='csv_wellformedness', error_type='error',
                                                  message=message, located_in='item', table=table))

                        elif not wellformedness_single_id(item):
                            message = messages['m2']
                            table = {row_idx: {field: [item_idx]}}
                            error_final_report.append(
                                create_error_dict(validation_level='csv_wellformedness', error_type='error',
                                                  message=message, located_in='item', table=table))

                        else:
                            # -------------ADD CHECK ON LEVEL 2 (EXTERNAL SYNTAX) AND 3 (SEMANTICS) FOR THE SINGLE IDs
                            pass



                if field == 'citing_publication_date' or field == 'cited_publication_date':
                    if not wellformedness_date(value):
                        message = messages['m3']
                        table = {row_idx: {field: [0]}}
                        error_final_report.append(
                            create_error_dict(validation_level='csv_wellformedness', error_type='error',
                                              message=message, located_in='item', table=table))

pprint(error_final_report, sort_dicts=False)
# print(error_final_report)