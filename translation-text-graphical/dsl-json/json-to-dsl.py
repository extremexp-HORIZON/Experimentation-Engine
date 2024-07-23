import json
import textx

def json_to_dsl(json_data):
    dsl_lines = []

    nodes = {node['id']: node for node in json_data['nodes']}

    start_node = next(node for node in nodes.values() if node['type'] == 'start')
    end_node = next(node for node in nodes.values() if node['type'] == 'end')


    dsl_lines.append(f'workflow simple {{')


    task_names = []

    for node in json_data['nodes']:
        if node['type'] == 'task':
            task_name = node['data']['variants'][0]['name'].replace(" ", "")
            task_names.append(task_name)
            dsl_lines.append(f'    define task {task_name};')
            dsl_lines.append(f'    configure task {task_name}{{}}')

    id_to_task_name = {node['id']: node['data']['variants'][0]['name'].replace(" ", "") for node in json_data['nodes']
                       if node['type'] == 'task'}


    connection_line = "START"
    current_node = start_node

    while current_node['id'] != end_node['id']:
        next_edge = next(edge for edge in json_data['edges'] if edge['source'] == current_node['id'])
        next_node = nodes[next_edge['target']]

        if next_node['type'] == 'task':
            connection_line += f' -> {id_to_task_name[next_node["id"]]}'
        current_node = next_node

    connection_line += ' -> END'
    dsl_lines.append(f'{connection_line};')

    dsl_lines.append('}')

    return '\n'.join(dsl_lines)

def parse_dsl(dsl):
    workflow_metamodel = textx.metamodel_from_file('workflow_grammar.tx')
    workflow_model = workflow_metamodel.model_from_str(dsl)

    if workflow_model:
        print("Successfully Parsed!")



with open('../json-dsl/simple-experiment.json', 'r') as file:
    json_data = json.load(file)

dsl_output = json_to_dsl(json_data)
print(dsl_output)

parse_dsl(dsl_output)
