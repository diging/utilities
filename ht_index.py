from elasticsearch import *
import json
import getopt


INDEX_NAME = 'hathi_trust'
ELASTIC_HOST = 'localhost'
ELASTIC_PORT = 9200

def create_index(es_object, index_name=INDEX_NAME):
    created = False
    # index settings
    with open('mapping.json') as f:
        settings =  json.load(f)

    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=index_name,  body=settings)
            print('[Success] Index created')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created

def store_record(elastic_object, record, index_name=INDEX_NAME):
    try:
        outcome = elastic_object.index(index=index_name, doc_type='publication', body=record)
    except Exception as ex:
        print('[Error] Error in indexing record')
        print(str(ex))

field_dict = {
    '010': [('loc_control_number', 'a')],
    '100': [('main_personal_name', 'a'), ('main_personal_titles', 'c'), ('main_personal_dates', 'd'), ('main_personal_date_of_work', 'f'), ('main_personal_fuller_name', 'q'), ('main_personal_affiliation', 'u'), ('main_personal_other', 'g-R')],
    '110': [('corporate_name', 'a'), ('corporate_dates', 'd-R'), ('corporate_location', 'c-R'), ('corporate_subordinate_unit', 'b-R')],
    '111': [('meeting_name', 'a'), ('meeting_date', 'd-R'), ('meeting_place', 'c-R'), ('meeting_subordinate_unit', 'e-R')],
    '130': [('main_uniform_title', 'a'), ('main_uniform_date_treaty_signed', 'd-R'), ('main_uniform_date', 'f'), ('main_uniform_language', 'l')],
    '210': [('abbreviated_title', 'a-R')],
    '222': [('key_title', 'a-R')],
    '240': [('uniform_title', 'a'), ('uniform_title_date_treaty_signed', 'd-R'), ('uniform_title_date_of_work', 'f')],
    '242': ('title_translation', [('title', 'a'), ('remainder', 'b'), ('responsibility', 'c')]),
    '243': [('collective_uniform_title', 'a'), ('collective_uniform_title_date_treaty_signed', 'd-R'), ('collective_uniform_title_date_of_work', 'f')],
    '245': [('title_statement', 'a'), ('title_statement_remainder', 'b'), ('title_statement_responsibility', 'c'), ('title_statement_dates', 'f')],
    '246': ('varying_title', [('title', 'a'), ('remainder', 'b'), ('date', 'f')]),
    '247': ('former_title', [('title', 'a'), ('remainder', 'b'), ('date', 'f')]),
    '250': ('edition', [('edition', 'a'), ('remainder', 'b')]),
    '251': ('version', [('version', 'a-R')]),
    '254': ('musical_presentation_statement', [('statement', 'a')]),
    '255': ('cartographical_math_data', [('scale', 'a'), ('projection', 'b'), ('coordinates', 'c'), ('zone', 'd'), ('equinox', 'e'), ('outer_gring', 'f'), ('exclusion_gring', 'g')]),
    '256': [('computer_file_characteristics', 'a')],
    '257': ('country_producing_entity', [('country', 'a-R')]),
    '260': ('publication_info', [('place', 'a-R'), ('name', 'b-R'), ('date', 'c-R'), ('manufacture_place', 'e-R'), ('manufacture', 'f-R'), ('manufacture_date', 'g-R')]),
    '263': [('projected_pub_date', 'a')],
    '264': ('production', [('place', 'a-R'), ('name', 'b-R'), ('date', 'c-R')]),
    '270': ('address', [('address', 'a-R'), ('city', 'b'), ('state', 'c'), ('country', 'd'), ('zip', 'e')]),
    '300': [('extend', 'a-R')],
    '306': [('playing_time', 'a-R')],
    '310': [('pub_frequency', 'a')],
    '321': [('former_pub_frequency', 'a'), ('former_pub_frequency_dates', 'b')],
    '336': [('content_type', 'a-R')],
    '336': [('media_type', 'a-R')],
    '380': [('form_of_work', 'a-R')],
    '388': [('creation_time_period', 'a-R')],
    '490': ('series', [('statement', 'a-R'), ('volume', 'v-R'), ('loc_call_number', 'l'), ('international_serial', 'x-R')]),
    '5XX': [('note', 'a-R')],
    '600': ('subjects_personal', [('name', 'a'), ('numeration', 'b'), ('titles', 'c-R'), ('date', 'd'), ('relator', 'e-R'), ('date_of_work', 'f'), ('other', 'g-R')]),
    '610': ('subjects_corporate', [('name', 'a'), ('subordinate_unit', 'b-R'), ('location', 'c-R'), ('date', 'd-R'), ('relator', 'e-R'), ('date_of_work', 'f'), ('other', 'g-R')]),
    '611': ('subjects_meeting', [('name', 'a'), ('subordinate_unit', 'e-R'), ('location', 'c-R'), ('date', 'd-R'), ('date_of_work', 'f'), ('other', 'g-R')]),
    '630': ('subjects_uniform_title', [('title', 'a'), ('date', 'd-R'), ('relator', 'e-R'), ('date_of_work', 'f'), ('other', 'g-R')]),
    '647': ('subjects_event', [('form_subdivision', 'v-R'), ('general_subdivision', 'x-R'), ('chrono_subdivision', 'y-R'), ('geo_subdivision', 'z-R')]),
    '648': ('subjects_chronological_term', [('chrono_term', 'a'), ('form_subdivision', 'v-R'), ('general_subdivision', 'x-R'), ('chrono_subdivision', 'y-R'), ('geo_subdivision', 'z-R')]),
    '650': ('subjects_topical_term', [('term', 'a'), ('term_following', 'b'), ('location', 'c'), ('dates', 'd'), ('relator', 'e-R'), ('other', 'g-R'), ('form_subdivision', 'v-R'), ('general_subdivision', 'x-R'), ('chrono_subdivision', 'y-R'), ('geo_subdivision', 'z-R')]),
    '651': ('subjects_geo_term', [('name', 'a'), ('relator', 'e-R'), ('other', 'g-R'), ('form_subdivision', 'v-R'), ('general_subdivision', 'x-R'), ('chrono_subdivision', 'y-R'), ('geo_subdivision', 'z-R')]),
    '653': [('index_term_uncontrolled', 'a-R')],
    '654': ('subjects_faceted_topical_term', [('focus_term', 'a-R'), ('non_focus_term', 'b-R'), ('hierarchy', 'c-R'), ('relator', 'e-R'), ('form_subdivision', 'v-R'), ('chrono_subdivision', 'y-R'), ('geo_subdivision', 'z-R')]),
    '655': ('index_term_genre', [('focus_term', 'a'), ('non_focus_term', 'b-R'), ('hierarchy', 'c-R'), ('form_subdivision', 'v-R'), ('general_subdivision', 'x-R'),('chrono_subdivision', 'y-R'), ('geo_subdivision', 'z-R')]),
    '656': ('index_term_occupation', [('occupation', 'a'), ('form', 'k'), ('form_subdivision', 'v-R'), ('general_subdivision', 'x-R'),('chrono_subdivision', 'y-R'), ('geo_subdivision', 'z-R')]),
    '657': ('index_term_function', [('function', 'a'), ('form_subdivision', 'v-R'), ('general_subdivision', 'x-R'),('chrono_subdivision', 'y-R'), ('geo_subdivision', 'z-R')]),
    '658': ('index_term_curriculum_objective', [('main_objective', 'a'), ('sub_objective', 'b-R'), ('code', 'c'), ('corr_factor', 'd')]),
    '662': ('subjects_hierach_place_name', [('country', 'a-R'), ('first_political_jur', 'b'), ('interm_political_jur', 'c-R'), ('city', 'd'), ('relator', 'e-R'), ('city_subsection', 'f-R'), ('other', 'g-R'), ('extraterrestrial', 'h-R')]),
    '69X': [('subjects_local', 'a-R')],
    '700': ('added_entry_personal', [('name', 'a'), ('numeration', 'b'), ('titles', 'c-R'), ('dates', 'd'), ('relator', 'e-R'), ('other', 'g-R'), ('fuller_form', 'q'), ('affiliation', 'u')]),
    '710': ('added_entry_corporate', [('name', 'a'), ('subordinate_unit', 'b-R'), ('location', 'c-R'), ('date', 'd-R'), ('relator', 'e-R'), ('other', 'g-R'), ('affiliation', 'u')]),
    '711': ('added_entry_meeting', [('name', 'a'), ('location', 'c-R'), ('date', 'd-R'), ('subordinate_unit', 'e-R'), ('other', 'g-R'), ('relator', 'j-R'), ('affiliation', 'u')]),
    '720': ('added_entry_uncontrolled', [('name', 'a'), ('relator', 'e-R')]),
    '730': ('added_entry_uniform_title', [('title', 'a'), ('date', 'd-R'), ('other', 'g-R')]),
    '740': [('added_entry_uncontrolled_title', 'a-R')],
    '751': ('added_entry_geo_name', [('name', 'a'), ('relator', 'e-R')]),
    '752': ('added_entry_hierach_place_name', [('country', 'a-R'), ('first_political_jur', 'b'), ('interm_political_jur', 'c-R'), ('city', 'd'), ('relator', 'e-R'), ('city_subsection', 'f-R'), ('other', 'g-R'), ('extraterrestrial', 'h-R')]),
    '754': ('added_entry_taxonomic_ident', [('name', 'a-R'), ('category', 'c-R'), ('common_name', 'd-R'), ('non_public_note', 'x-R'), ('public_note', 'z-R')]),
    '758': [('resource_ident', 'a-R')],
    '760': ('main_series', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '762': ('subseries', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '770': ('supplement_special_issue', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '772': ('supplement_parent_issue', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '773': ('host_item', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '774': ('constituent_unit', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '775': ('other_edition', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '777': ('issued_with', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '786': ('data_source', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '787': ('other_relationship', [('heading', 'a'), ('edition', 'b'), ('qualifying_info', 'c'), ('place_pub_date', 'd'), ('related_parts', 'g-R'), ('note', 'n-R'), ('uniform_title', 's'), ('title', 't'), ('issn', 'x')]),
    '800': ('series_added_entry_personal', [('name', 'a'), ('numeration', 'b'), ('titles', 'c-R'), ('dates', 'd'), ('relator', 'e-R'), ('other', 'g-R'), ('fuller_name', 'q'), ('affiliation', 'u')]),
    '810': ('series_added_entry_corporate', [('name', 'a'), ('subordinate_unit', 'b-R'), ('location', 'c-R'), ('date', 'd-R'), ('relator', 'e-R'), ('date_of_work', 'f'), ('other', 'g-R')]),
    '811': ('series_added_entry_meeting', [('name', 'a'), ('location', 'c-R'), ('date', 'd-R'), ('subordinate_unit', 'e-R'), ('date_of_work', 'f'), ('other', 'g-R'), ('relator', 'j-R')]),
    '830': ('series_added_uniform_title', [('title', 'a'), ('date', 'd-R'), ('date_of_work', 'f'), ('other', 'g-R'), ('title_of_work', 't'), ('volume', 'v')]),
    '970': [('document_type', 'a')],
    '974': [('hathi_id', 'u')],
}

def create_indexable_json(line):
    def get_from_subfield(field, subfield_name):
        subfields = field['subfields']
        for subfield in subfields:
            for sk, sv in subfield.items():
                if sk == subfield_name:
                    return sv

    line_as_json = json.loads(line)
    metadata_dict = {}

    def add_to_list(meta_dict, code, key, subfield):
        field_value = None
        if code.endswith('-R'):
            code = code[:-2]
            if key not in meta_dict:
                meta_dict[key] = []

            field_value = meta_dict[key]

        value_from_subfield = get_from_subfield(subfield, code)
        # skip if there is no value for this subfield
        if not value_from_subfield:
            return

        if type(field_value) != list:
            meta_dict[key] = value_from_subfield
        else:
            meta_dict[key].append(value_from_subfield)

    fields = line_as_json['fields']
    for field in fields:
        for k, v in field.items():
            if k not in field_dict:
                continue

            # let's put all notes in one field
            if k.startswith('5'):
                k = '5XX'
            # let's put all local subjects in one list
            if k.startswith('69'):
                k = '69X'
            fields = field_dict[k]

            # just one entry (NR)
            if type(fields) == list:
                for entry in fields:
                    add_to_list(metadata_dict, entry[1], entry[0], v)
                continue

            # multiple entries possible/repeatable (indicated by (R) in MARC explanation)
            field_main = fields[0]
            if field_main not in metadata_dict:
                metadata_dict[field_main] = []

            fields_sub = {}
            for subfield in fields[1]:
                add_to_list(fields_sub, subfield[1], subfield[0], v)

            metadata_dict[field_main].append(fields_sub)

    return metadata_dict

######################### This is where the action happens ##################

def main(arguments):

    options, remainder = getopt.getopt(arguments, 'i:h:p:', ['input=',
                                                             'host=',
                                                             'port=',
                                                             ])
    host = ELASTIC_HOST
    port = ELASTIC_PORT
    filepath = ''

    for opt, arg in options:
        if opt in ('-i', '--input'):
            filepath = arg
        elif opt in ('-h', '--host'):
            host = arg
        elif opt in ('-p', '--port'):
            port = arg

    if not filepath:
        print "[ERROR] No input file provided. Please specify an input file using -i or --input."
        return

    print "[INFO] Importing " + filepath
    print "[INFO] Using Elasticsearch at %s:%s"%(host, port)

    _es = Elasticsearch([{'host': host, 'port': port}])
    create_index(_es)

    with open(filepath) as fp:
       line = fp.readline()
       cnt = 1
       while line:
           j_line = create_indexable_json(line)
           store_record(_es, j_line)
           print "[SUCCESS] Indexed line " + str(cnt)
           line = fp.readline()
           cnt += 1


###########

main(sys.argv[1:])