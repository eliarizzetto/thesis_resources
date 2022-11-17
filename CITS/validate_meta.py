# This file contains the base structure wherein to call the validation functions for META-CSV.

from helper_functions import content, group_ids, check_fieldnames_meta
from validation_functions import wellformedness_id_field, wellformedness_br_id, wellformedness_date
from create_report import create_error_dict
# from check_output.check_validation_output import check_validation_output
import re
from pprint import pprint
import yaml
from csv import DictReader
from get_duplicates import get_duplicates_cits

csv_doc = 'C:/Users/media/Desktop/thesis23/thesis_resources/validation_process/validation/test_files/test_0.csv'


def validate_meta(csv_doc: str) -> list:
    """
    Validates META-CSV.
    :param csv_doc
    :return: the list of error, i.e. the report of the validation process
    """
    with open(csv_doc, 'r', encoding='utf-8') as f:
        data_dict = list(DictReader(f))

        # TODO: Handling strategy for the error here below, which doesn't allow further processing!
        if not check_fieldnames_meta(data_dict):  # check fieldnames
            raise KeyError

        error_final_report = []

        messages = yaml.full_load(open('messages.yaml', 'r', encoding='utf-8'))

        br_id_groups = []
        ra_id_groups = []

        for row_idx, row in enumerate(data_dict):

            # TODO: CONSIDER INITIALIZING A DICTIONARY FOR LATER CHECKING REQUIRED FIELDS IN ROW. A proper value for
            #  each visited field of the row would be added here, and later the conditional requirements would be
            #  checked, right before the closure of the loop for this row. The default behaviour in visiting single
            #  fields would be: if not content -> add proper value in the dict

            for field, value in row.items():
                if field == 'id':

                    # if not content(value):  # Check required fields
                    #     message = messages['m7']
                    #     table = {row_idx: {field: None}}
                    #     error_final_report.append(
                    #         create_error_dict(validation_level='csv_wellformedness', error_type='error',
                    #                           message=message, error_label='required_value_cits', located_in='field',
                    #                           table=table))

                    br_ids_set = set()  # set where to put valid br IDs only
                    items = re.split(r'\s', value)

                    for item_idx, item in enumerate(items):

                        if item == '':
                            message = messages['m1']
                            table = {row_idx: {field: [item_idx]}}
                            error_final_report.append(
                                create_error_dict(validation_level='csv_wellformedness', error_type='error',
                                                  message=message, error_label='extra_space', located_in='item',
                                                  table=table))

                        elif not wellformedness_br_id(item):
                            message = messages['m2']
                            table = {row_idx: {field: [item_idx]}}
                            error_final_report.append(
                                create_error_dict(validation_level='csv_wellformedness', error_type='error',
                                                  message=message, error_label='br_id_format', located_in='item',
                                                  table=table))

                        else:
                            # TODO: ADD CHECK ON LEVEL 2 (EXTERNAL SYNTAX) AND 3 (SEMANTICS) FOR THE SINGLE IDs

                            if item not in br_ids_set:
                                br_ids_set.add(item)
                            else:  # in-field duplication of the same ID
                                table = {row: {field: [i for i, v in enumerate(item) if v == item]}}
                                message = messages['m6']

                                error_final_report.append(
                                    create_error_dict(validation_level='csv_wellformedness', error_type='error',
                                                      message=message, error_label='duplicate_id', located_in='item',
                                                      table=table)  # valid=False
                                )

                    if len(br_ids_set) >= 1:
                        br_id_groups.append(br_ids_set)

                if field == 'title':
                    if value.isupper():
                        message = messages['m8']
                        table = {row_idx: {field: [0]}}
                        error_final_report.append(
                            create_error_dict(validation_level='csv_wellformedness', error_type='warning',
                                              message=message, error_label='uppercase_title', located_in='item',
                                              table=table, valid=True))

                if field == 'author':
                    pass # TODO: find strategy to divide all RA fields into items!


                if field == 'pub_date':
                    # todo: consider splitting into items also some one-item fields, like the ones for the date,
                    #  in order to identify the error location more precisely (for example, in case of extra spaces)
                    if content(value):
                        if not wellformedness_date(value):
                            message = messages['m3']
                            table = {row_idx: {field: [0]}}
                            error_final_report.append(
                                create_error_dict(validation_level='csv_wellformedness', error_type='error',
                                                  message=message, error_label='date_format', located_in='item',
                                                  table=table))

        # GET BIBLIOGRAPHIC ENTITIES
        br_entities = group_ids(br_id_groups)
        ra_entities = group_ids(ra_id_groups)

        # TODO: find duplicates for META-CSV and change this part!!
        # GET SELF-CITATIONS AND DUPLICATE CITATIONS (returns the list of error reports)
        # duplicate_report = get_duplicates_cits(entities=br_entities, data_dict=data_dict, messages=messages)
        #
        # if duplicate_report:
        #     error_final_report.extend(duplicate_report)

        return error_final_report


pprint(validate_meta(csv_doc))
