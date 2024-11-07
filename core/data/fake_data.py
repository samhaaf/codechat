from faker import Faker
import json
import uuid
from datetime import datetime
import random
import sys
from pprint import pprint
import copy
import itertools

def convert_to_serializable(data):
    if isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, (uuid.UUID, datetime)):
        return str(data)
    else:
        return data


def generate_data(field_config, foreign_keys={}):
    # Check for null_probability and decide if this field should be null
    if random.random() < field_config.get('null_probability', 0):
        return None

    # Check if the field has a foreign key
    if 'foreign_key' in field_config:
        if random.random() > field_config.get('probability', 1):
            return None
        return foreign_keys.get(field_config['foreign_key'])

    # Implement the "choice" type
    if 'choice' in field_config:
        options = field_config['choice']['options']
        probabilities = field_config['choice'].get('probability', [1 / len(options) for _ in options])
        chosen_option = random.choices(options, probabilities, k=1)[0]
        return generate_data(chosen_option, foreign_keys)

    if field_config.get('type') == 'json':
        return dict({key: generate_data(value, foreign_keys) for key, value in field_config['format'].items()})

    if 'num_values' in field_config:
        _field_config = copy.deepcopy(field_config)
        del _field_config['num_values']
        return [generate_data(_field_config, foreign_keys) for _ in range(field_config['num_values'])]

    if 'type' not in field_config:
        if 'value' in field_config:
            return field_config['value']
        else:
            raise RuntimeError(f'Unhandled config definition: {field_config}')

    fake = Faker()

    if field_config['type'] == 'uuid':
        return str(uuid.uuid4())
    elif field_config['type'] == 'timestamptz' or field_config['type'] == 'timestamp':
        return fake.date_time_this_decade()
    elif field_config['type'] == 'varchar' or field_config['type'] == 'text':
        return fake.text(max_nb_chars=200)
    elif field_config['type'] == 'bigint':
        return fake.random_int(min=0, max=9223372036854775807)
    elif field_config['type'] == 'integer':
        return fake.random_int(min=0, max=2147483647)
    elif field_config['type'] == 'boolean':
        return fake.boolean()
    elif field_config['type'] == 'real':
        return fake.pyfloat(left_digits=5, right_digits=5, positive=True)
    else:
        raise RuntimeError(f'Unhandled field type: {field_config["type"]}')


def generate_foreign_key_combinations(key_list, output):
    tables = set()
    fields = {}
    for key in key_list:
        table, field = key.split('.')
        tables.add(table)
        fields.setdefault(table, []).append((key, field))

    unzipped = []
    for table in tables:
        for key, field in fields[table]:
            field_array = [{key: record[field]} for record in output[table]]
            unzipped.append(field_array)

    record_pairs = [
         {k: v for d in field_dicts for k, v in d.items()}
         for field_dicts in zip(*unzipped)
    ]

    return record_pairs


def generate_from_config(config):
    output = {}
    for table_config in config:
        table_name = table_config['table']
        if table_name not in output:
            output[table_name] = []

        records = output[table_name]

        for _ in range(table_config.get('num', 1)):
            if 'for_each' in table_config:
                if not all(isinstance(item, list) for item in table_config['for_each']):
                    table_config['for_each'] = [table_config['for_each']]
                for key_list in table_config['for_each']:
                    foreign_key_combos = generate_foreign_key_combinations(key_list, output)
                    for foreign_keys in foreign_key_combos:
                        if random.random() > table_config.get('probability', 1):
                            continue
                        records.append({
                            field_name: generate_data(field_config, foreign_keys)
                            for field_name, field_config in table_config['fields'].items()
                        })
            else:
                records.append({
                    field_name: generate_data(field_config)
                    for field_name, field_config in table_config['fields'].items()
                })

        output[table_name] = records

    return output

if __name__ == '__main__':
    with open('fake_data_config.json', 'r') as f:
        data_config = json.load(f)

    print('Generating fake data...')
    output = generate_from_config(data_config)

    json_blob = json.dumps(convert_to_serializable(output), indent=4)

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'w') as f:
            f.write(json_blob)
        print('Record counts:')
        pprint([[k, len(v)] for k, v in output.items()])
    else:
        print(json_blob)
