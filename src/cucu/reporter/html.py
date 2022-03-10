import glob
import jinja2
import shutil
import os
import urllib
import json


def generate(results,
             basepath):
    """
    generate an HTML report for the results provided.
    """
    run_json_filepath = os.path.join(results, 'run.json')
    features = []

    with open(run_json_filepath, 'rb') as index_input:
        features = json.loads(index_input.read())

    #
    # augment existing test run data with:
    #  * features & scenarios with `duration` attribute computed by adding all
    #    step durations.
    #  * add `image` attribute to a step if it has an underlying .png image.
    #
    for index in range(0, len(features)):
        feature = features[index]
        scenarios = feature['elements']
        feature_duration = 0

        if feature['status'] != 'skipped':
            # copy each feature directories contents over to the report directory
            src_feature_filepath = os.path.join(results, feature['name'])
            dst_feature_filepath = os.path.join(basepath, feature['name'])
            shutil.copytree(src_feature_filepath, dst_feature_filepath, dirs_exist_ok=True)

        for scenario in scenarios:
            scenario_duration = 0
            scenario_filepath = os.path.join(basepath,
                                             feature['name'],
                                             scenario['name'])

            step_index = 0
            for step in scenario['steps']:
                image_filename = f"{step_index} - {step['name'].replace('/', '_')}.png"
                image_filepath = os.path.join(scenario_filepath, image_filename)

                if os.path.exists(image_filepath):
                    step['image'] = urllib.parse.quote(image_filename)

                if 'result' in step:
                    scenario_duration += step['result']['duration']

                step_index += 1
            logs_filepath = os.path.join(scenario_filepath, 'logs')

            if os.path.exists(logs_filepath):
                log_files = glob.iglob(os.path.join(logs_filepath, '*.*'))
                log_files = [
                    {
                        'filepath': log_file.replace(f'{scenario_filepath}/', ''),
                        'name': os.path.basename(log_file)
                    }
                    for log_file in log_files
                ]
                scenario['logs'] = log_files

            scenario['duration'] = scenario_duration
            feature_duration += scenario_duration

        feature['duration'] = feature_duration

    package_loader = jinja2.PackageLoader('cucu.reporter', 'templates')
    templates = jinja2.Environment(loader=package_loader)

    index_template = templates.get_template('index.html')
    rendered_index_html = index_template.render(features=features,
                                                title='Cucu HTML Test Report',
                                                basepath=basepath)

    index_output_filepath = os.path.join(basepath, 'index.html')
    with open(index_output_filepath, 'wb') as output:
        output.write(rendered_index_html.encode('utf8'))

    feature_template = templates.get_template('feature.html')

    for feature in features:
        feature_basepath = os.path.join(basepath, feature['name'])
        if not os.path.exists(feature_basepath):
            os.makedirs(feature_basepath)

        scenarios = feature['elements']
        rendered_feature_html = feature_template.render(feature=feature,
                                                        scenarios=scenarios)

        feature_output_filepath = os.path.join(basepath,
                                               f'{feature["name"]}.html')

        with open(feature_output_filepath, 'wb') as output:
            output.write(rendered_feature_html.encode('utf8'))

        scenario_template = templates.get_template('scenario.html')

        for scenario in scenarios:
            steps = scenario['steps']
            scenario_basepath = os.path.join(feature_basepath, scenario['name'])

            if not os.path.exists(scenario_basepath):
                os.makedirs(scenario_basepath)

            scenario_output_filepath = os.path.join(scenario_basepath,
                                                    'index.html')

            rendered_scenario_html = scenario_template.render(basepath=results,
                                                              feature=feature,
                                                              path_exists=os.path.exists,
                                                              scenario=scenario,
                                                              steps=steps)

            with open(scenario_output_filepath, 'wb') as output:
                output.write(rendered_scenario_html.encode('utf8'))

    return os.path.join(basepath, 'index.html')
