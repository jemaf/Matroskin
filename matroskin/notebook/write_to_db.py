from typing import Dict

from ..connector import db_structures


def write_notebook_to_db(conn, nb_metadata, cells):
    ntb = db_structures.NotebookDb(
        notebook_name=nb_metadata['name'],
        notebook_language=nb_metadata['language'],
        notebook_version=nb_metadata['version'],
    )

    exists = (conn.query(db_structures.NotebookDb).
        filter_by(notebook_name=nb_metadata['name']).one())

    if not exists:
        conn.add(ntb)
        conn.commit()
    else:
        ntb.notebook_id = exists.notebook_id
        
    conn = write_cells_to_db(conn, cells, ntb.notebook_id)
    return ntb.notebook_id


def write_features_to_db(conn, nb_metadata, features):
    nbf = db_structures.NotebookFeaturesDb(
        notebook_id=nb_metadata['id']
    )
    cell_flatten = flatten(features)
    for key in cell_flatten.keys():
        cell_attributes = [name for name in dir(nbf)
                           if not name.startswith('_')]
        if key in cell_attributes:
            setattr(nbf, key, cell_flatten[key])

    conn.merge(nbf)
    conn.commit()

    return cell_flatten


def write_cells_to_db(conn, cells, notebook_id):  
    for cell in cells:
        cell_db = db_structures.CellDb(notebook_id=notebook_id, 
                                       cell_id=cell.get('cell_id'))
        conn.merge(cell_db)
        conn.flush()
        
        processed_cell_db = process_cell(cell)
        processed_cell_db.notebook_id = cell_db.notebook_id
        processed_cell_db.cell_id = cell_db.cell_id
        conn.merge(processed_cell_db)
        conn.flush()
        
    conn.commit()
    return conn


def flatten(dictionary) -> Dict:
    """
    This function makes dictionary flattening by following rule:
    example_dict = {
                "test1": "string here",
                "test2": "another string",
                "test3": {
                        "test4": 25,
                        "test5": {
                                  "test7": "very nested."
                        },
                        "test6": "yep, another string"
                },
    }

    To

    resulting_dict = {
                "test1": "string here",
                "test2": "another string",
                "test4": 25,
                "test7": "very nested.",
                "test6": "yep, another string"
    }

    And returns flattened dictionary
    """

    output = dict()
    for key, value in dictionary.items():
        if isinstance(value, dict):
            output.update(flatten(value))
        else:
            output[key] = value

    return output


def process_cell(cell):
    if cell['type'] == 'markdown':
        cell_db = db_structures.MdCellDb(
            cell_num=cell['num'],
            source=cell['source']
        )
    else:
        cell_db = db_structures.CodeCellDb(
            cell_num=cell['num'],
            source=cell['source']
        )

    cell_flatten = flatten(cell)
    for key in cell_flatten.keys():
        cell_attributes = [name for name in dir(cell_db)
                           if not name.startswith('_')]
        if key in cell_attributes:
            setattr(cell_db, key, cell_flatten[key])

    return cell_db
