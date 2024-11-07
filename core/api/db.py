import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from graphene_sqlalchemy import SQLAlchemyObjectType

import re


from .config import Config


# get the connection details from environment variables
DATABASE_USER = Config.DATABASE_USER
DATABASE_PASS = Config.DATABASE_PASS
DATABASE_HOST = Config.DATABASE_HOST
DATABASE_PORT = Config.DATABASE_PORT
DATABASE_NAME = Config.DATABASE_NAME

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?options=-c%20search_path%3Dlogscale"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Update the graphene_sqlalchemy object to use uid instead of id
def get_node_by_uid(cls, info, uid):
    return info.context.get_session().query(cls._meta.model).filter_by(uid=uid).first()

SQLAlchemyObjectType.get_node = classmethod(get_node_by_uid)



# dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sql_connection():
    """ Create a database connection and return the connection object """
    try:
        conn = psycopg2.connect(
            user = DATABASE_USER,
            password = DATABASE_PASS,
            host = DATABASE_HOST,
            port = DATABASE_PORT,
            dbname = DATABASE_NAME
        )
        return conn
    except OperationalError as e:
        print(f"Error: {e}")
        return None


def process_query_template(template, values):
    """
    Process a query template with placeholders and replace them with appropriate SQL constructs.
    Also, build a list of values to be used in query execution.

    Args:
    template (str): The query template with placeholders.
    values (list or dict): The values to be inserted into the query.

    Returns:
    tuple: The processed query and the list of values.
    """

    def columns_format(values):
        if isinstance(values, dict):
            keys = sorted(list(values.keys()))
            return ', '.join(keys), []
        elif isinstance(values, list):
            unique_keys = sorted(list(set(key for val_dict in values for key in val_dict.keys())))
            all_values = [[val_dict.get(key) for key in unique_keys] for val_dict in values]
            return ', '.join(unique_keys), []

    def values_format(values):
        if isinstance(values, dict):
            keys = sorted(list(values.keys()))
            placeholders = '(' + ', '.join(['%s'] * len(keys)) + ')'
            return placeholders, [values[key] for key in keys]
        elif isinstance(values, list):
            unique_keys = sorted(list(set(key for val_dict in values for key in val_dict.keys())))
            placeholders = '(' + ', '.join(['%s'] * len(unique_keys)) + ')'
            statement = ', '.join([placeholders] * len(values))
            all_values = [[val_dict.get(key) for key in unique_keys] for val_dict in values]
            flattened_values = [item for sublist in all_values for item in sublist]
            return statement, flattened_values

    def condition_format(values, join_operator):
        if not isinstance(values, dict):
            raise SyntaxError(f'${join_operator}(%s) value is expected to be a dict')
        keys = list(values.keys())
        conditions = f" {join_operator} ".join([f"({k} = %s)" for k in keys])
        return conditions, [values[k] for k in keys]

    def set_format(values):
        if not isinstance(values, dict):
            raise SyntaxError('$set(%s) value is expected to be a dict')
        keys = list(values.keys())
        setters = ', '.join([f"{k} = %s" for k in keys])
        return setters, [values[k] for k in keys]

    # Dictionary mapping placeholders to processing functions
    processors = {
        'columns': columns_format,
        'values': values_format,
        'and': lambda args: condition_format(args, 'AND'),
        'or': lambda args: condition_format(args, 'OR'),
        'set': set_format
    }

    # Error check for ambiguous placeholders
    if '%s' in template and re.search(r'%\d+', template):
        raise ValueError("Mix of %s and %[0-9]+ placeholders is ambiguous")

    # Find all matches for both patterns
    function_matches = [
        ((match.start(), match.end()), match.group(2), match.group(3))
        for match in re.finditer(rf'(\$({"|".join(processors.keys())})\((%s|%\d+)\))', template)
    ]
    matched_indices = set()
    for (start, end), _, _ in function_matches:
        matched_indices.update(range(start, end))
    placeholder_matches = [
        ((match.start(), match.end()), None, None)
        for match in re.finditer(r'(%s)', template)
        if match.start() not in matched_indices
    ]

    # Combine and sort matches by the starting index
    function_spans = sorted(function_matches + placeholder_matches, key=lambda x: x[0][0])

    new_template = ''
    index = 0
    query_values = []
    value_index = 0  # To keep track of %s placeholders
    using_value_index = False


    for span, function_name, arg_str in function_spans:
        print(span, function_name, arg_str)
        # if span == (-1, -1):
        #     continue
        start, end = span
        start_adjusted, end_adjusted = start - index, end - index

        new_template += template[:start_adjusted]

        if function_name is None:
            using_value_index = True
            # Handling lone %s placeholders
            if value_index >= len(values):
                raise ValueError("Not enough values for %s placeholders")
            query_values.append(values[value_index])
            value_index += 1
            new_template += '%s'
        else:
            # Process each argument and replace placeholders with values
            args = []
            for arg in arg_str.split(','):
                if arg.strip() == '%s':
                    using_value_index = True
                    if value_index >= len(values):
                        raise ValueError("Not enough values for %s placeholders")
                    args.append(values[value_index])
                    value_index += 1
                elif re.match(r'%\d+', arg.strip()):
                    pos = int(arg.strip()[1:])
                    if pos < 0 or pos >= len(values):
                        raise ValueError(f"Positional argument index {pos + 1} out of range")
                    args.append(values[pos])
                else:
                    args.append(arg.strip())

            # Calling the appropriate processor function with arguments
            processed_part, new_values = processors[function_name](*args)
            new_template += processed_part
            query_values.extend(new_values)

        template = template[end_adjusted:]
        index = end

    # Adding the remaining part of the template
    new_template += template

    # Error check if there are still unused values
    if using_value_index and value_index < len(values):
        raise ValueError("Some provided values were not used in the template")

    return new_template, query_values
