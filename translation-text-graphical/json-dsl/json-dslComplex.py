import textx
import json


def json_to_dsl(json_data):
    dsl_lines = []

    nodes = {node['id']: node for node in json_data['nodes']}
    edges = json_data['edges']

    # Define the workflow
    dsl_lines.append('workflow IDEKO_main {')

    # Define tasks
    for node in json_data['nodes']:
        if node['type'] == 'task':
            task_name = node['data']['variants'][0]['name'].replace(" ", "")
            dsl_lines.append(f'  define task {task_name};')

    dsl_lines.append('')

    # Task connections
    connection_line = '  // Task CONNECTIONS\n  START'
    current_node = next(node for node in nodes.values() if node['type'] == 'start')
    end_node = next(node for node in nodes.values() if node['type'] == 'end')

    while current_node['id'] != end_node['id']:
        next_edge = next(edge for edge in edges if edge['source'] == current_node['id'])
        next_node = nodes[next_edge['target']]
        if next_node['type'] == 'task':
            task_name = next_node['data']['variants'][0]['name'].replace(" ", "")
            connection_line += f' -> {task_name}'
        current_node = next_node

    connection_line += ' -> END;'
    dsl_lines.append(connection_line)

    dsl_lines.append('')

    # Configure tasks with their implementations
    for node in json_data['nodes']:
        if node['type'] == 'task':
            task_name = node['data']['variants'][0]['name'].replace(" ", "")
            implementation = node['data']['variants'][0]['implementationRef']
            dsl_lines.append(f'  configure task {task_name} {{')
            dsl_lines.append(f'    implementation "IDEKO-task-library.{implementation}";')
            dsl_lines.append(f'  }}')

    # Define input data
    for node in json_data['nodes']:
        if node['type'] == 'data':
            data_name = node['data']['name'].replace(" ", "")
            dsl_lines.append(f'\n  // DATA')
            dsl_lines.append(f'  define input data {data_name};')


    # Configure input data
    for node in json_data['nodes']:
        if node['type'] == 'data':
            data_name = node['data']['name'].replace(" ", "")
            dsl_lines.append(f'\n  configure data {data_name} {{')
            dsl_lines.append('    path "datasets/ideko-subset/**";')
            dsl_lines.append('  }}')

    dsl_lines.append('}')

    # Define variant workflows
    # for node in json_data['nodes']:
    #     if node['type'] == 'task' and 'variants' in node['data']:
    #         for variant in node['data']['variants']:
    #             if variant['variant'] > 1:
    #                 workflow_name = variant['id_task']
    #                 dsl_lines.append(f'\nworkflow {workflow_name} from IDEKO_main {{')
    #                 dsl_lines.append(f'  configure task {variant["name"].replace(" ", "")} {{')
    #                 dsl_lines.append(f'    implementation "IDEKO-task-library.{variant["implementationRef"]}";')
    #                 dsl_lines.append('  }')
    #                 dsl_lines.append('}')

    for node in json_data['nodes']:
        if node['type'] == 'task' and 'variants' in node['data']:
            if len(node['data']['variants']) > 1:
                for variant in node['data']['variants']:
                    workflow_name = variant['id_task']
                    dsl_lines.append(f'\nworkflow {workflow_name} from IDEKO_main {{')
                    dsl_lines.append(f'  configure task {variant["name"].replace(" ", "")} {{')
                    dsl_lines.append(f'    implementation "IDEKO-task-library.{variant["implementationRef"]}";')
                    dsl_lines.append('  }')
                    dsl_lines.append('}')

    # Define experiment
    dsl_lines.append('\nexperiment EXP {')
    dsl_lines.append('  intent FindBestClassifier;')
    dsl_lines.append('  control {')
    dsl_lines.append('    //Automated')
    dsl_lines.append('    S1')
    dsl_lines.append('  }')

    for node in json_data['nodes']:
        if node['type'] == 'task' and 'variants' in node['data']:
            if len(node['data']['variants']) > 1:
                for variant in node['data']['variants']:
                    workflow_name = variant['id_task']

                    dsl_lines.append(f'\n  space S{variant["variant"]} of {workflow_name} {{')
                    dsl_lines.append('    strategy gridsearch;')

                    for param in variant['parameters']:
                        param_name = param['name']
                        param_values = ', '.join(map(str, param['values']))
                        param_type = 'enum' if len(param['values']) == 1 else 'range'
                        dsl_lines.append(f'    param {param_name}_vp = {param_type}({param_values});')

                    dsl_lines.append(f'    configure task {variant["name"].replace(" ", "")} {{')
                    for param in variant['parameters']:
                        param_name = param['name']
                        dsl_lines.append(f'      param {param_name} = {param_name}_vp;')
                    dsl_lines.append('    }')
                    dsl_lines.append('  }')

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


# with open('expected.dsl', 'r') as file:
#     no_events_workflow_code = file.read()
#
# workflow_metamodel = textx.metamodel_from_file('../dsl/workflow_grammar_new.tx')
# no_events_workflow_model = workflow_metamodel.model_from_str(no_events_workflow_code)

# parse_dsl(dsl_output)
