from sqlalchemy import create_engine, Table, MetaData, select, and_, func, JSON, Column
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker

# Database connection setup
engine = create_engine('postgresql://user:password@localhost/dbname')
Session = sessionmaker(bind=engine)
session = Session()

# Metadata object to reflect existing database schema
metadata = MetaData()
metadata.reflect(bind=engine)

# Example tables, replace these with your actual table definitions
comp_data = Table('comp_data', metadata, autoload_with=engine)
comp_version = Table('comp_version', metadata, autoload_with=engine)
ehr_folder_data = Table('ehr_folder_data', metadata, autoload_with=engine)
ehr_folder_version = Table('ehr_folder_version', metadata, autoload_with=engine)
ehr_status_data = Table('ehr_status_data', metadata, autoload_with=engine)
ehr_status_version = Table('ehr_status_version', metadata, autoload_with=engine)

def build_sql_query(asl_root_query):
    # This function builds the SQL query from an ASL root query
    subqueries = []
    main_table = Table(asl_root_query['main_table'], metadata, autoload_with=engine)
    query = select([main_table])

    # Add select fields
    for field in asl_root_query['select_fields']:
        query = query.add_columns(main_table.c[field])

    # Add joins
    for join in asl_root_query.get('joins', []):
        child_table = Table(join['table'], metadata, autoload_with=engine)
        query = query.join(child_table, onclause=join['on_clause'], isouter=join.get('is_outer', False))

    # Add where conditions
    if 'conditions' in asl_root_query:
        conditions = [text(cond) for cond in asl_root_query['conditions']]
        query = query.where(and_(*conditions))

    # Add group by
    if 'group_by' in asl_root_query:
        query = query.group_by(*[main_table.c[field] for field in asl_root_query['group_by']])

    # Add order by
    if 'order_by' in asl_root_query:
        query = query.order_by(*[main_table.c[field] for field in asl_root_query['order_by']])

    # Add limit and offset
    if 'limit' in asl_root_query:
        query = query.limit(asl_root_query['limit'])
        if 'offset' in asl_root_query:
            query = query.offset(asl_root_query['offset'])

    return query

def explain_query(query, analyze=False):
    if analyze:
        explanation = session.execute(text("EXPLAIN (SUMMARY, COSTS, VERBOSE, FORMAT JSON, ANALYZE, TIMING) " + str(query)))
    else:
        explanation = session.execute(text("EXPLAIN (SUMMARY, COSTS, VERBOSE, FORMAT JSON) " + str(query)))
    return explanation.fetchall()

# Example usage
asl_root_query = {
    'main_table': 'comp_data',
    'select_fields': ['field1', 'field2'],
    'joins': [
        {'table': 'comp_version', 'on_clause': 'comp_data.id = comp_version.data_id'}
    ],
    'conditions': ['comp_data.status = "active"'],
    'group_by': ['field1'],
    'order_by': ['field2'],
    'limit': 10,
    'offset': 0
}

sql_query = build_sql_query(asl_root_query)
print(sql_query)
explanation = explain_query(sql_query, analyze=True)
print(explanation)
