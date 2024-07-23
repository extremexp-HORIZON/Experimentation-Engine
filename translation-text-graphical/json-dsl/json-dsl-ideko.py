import json
import textx

def json_to_dsl(json_data):
    dsl_lines = []

    nodes = {node['id']: node for node in json_data['nodes']}
    id_to_task_name = {node['id']: node['data']['variants'][0]['name'].replace(" ", "") for node in json_data['nodes']
                       if node['type'] == 'task'}


    dsl_lines.append(f'workflow IDEKO {{')

    for node in json_data['nodes']:
        if node['type'] == 'task':
            task_name = node['data']['variants'][0]['name'].replace(" ", "")
            dsl_lines.append(f'  define task {task_name};')

    start_node = next(node for node in nodes.values() if node['type'] == 'start')
    end_node = next(node for node in nodes.values() if node['type'] == 'end')

    connection_line = "START"
    current_node = start_node

    while current_node['id'] != end_node['id']:
        next_edge = next(edge for edge in json_data['edges'] if edge['source'] == current_node['id'])
        next_node = nodes[next_edge['target']]

        if next_node['type'] == 'task':
            connection_line += f' -> {id_to_task_name[next_node["id"]]}'
        current_node = next_node

    connection_line += ' -> END;'
    dsl_lines.append(f'  {connection_line}')

    for node in json_data['nodes']:
        if node['type'] == 'task':
            task_name = node['data']['variants'][0]['name'].replace(" ", "")
            implementation_name = node['data']['variants'][0]['implementationRef']
            dsl_lines.append(f'  configure task {task_name} {{')
            dsl_lines.append(f'      implementation "tasks/IDEKO/{implementation_name}.py";')
            dsl_lines.append(f'      dependency "tasks/IDEKO/src/**";')
            dsl_lines.append(f'  }}')

    dsl_lines.append('}')

    variants = [node for node in json_data['nodes'] if node['type'] == 'task' and len(node['data']['variants']) > 1]

    for node in variants:
        for variant in node['data']['variants']:
            variant_id = variant['id_task']
            variant_name = variant['name']
            task_name = node['data']['variants'][0]['name'].replace(" ", "")
            implementation_file = variant['implementationRef'].replace(" ", "_").lower() + ".py"

            dsl_lines.append(f'workflow {variant_id} from IDEKO {{')
            dsl_lines.append(f'  configure task {task_name} {{')
            dsl_lines.append(f'      implementation "tasks/IDEKO/{implementation_file}";')
            dsl_lines.append(f'  }}')
            dsl_lines.append(f'}}')

    return '\n'.join(dsl_lines)

def parse_dsl(dsl):
    workflow_metamodel = textx.metamodel_from_file('workflow_grammar_new.tx')
    workflow_model = workflow_metamodel.model_from_str(dsl)

    if workflow_model:
        print("Successfully Parsed!")



with open('imported-experiment.json', 'r') as file:
    json_data = json.load(file)

dsl_output = json_to_dsl(json_data)
print(dsl_output)

with open('expected.dsl', 'r') as file:
    dsl = file.read()

with open('actual.dsl', 'w') as file:
    file.write(dsl_output)

parse_dsl(dsl_output)