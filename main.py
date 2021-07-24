import argparse
import subprocess
import os
import json
import sys
import k8s_manifests


def run_command(cmd, output=False):
    if output:
        return subprocess.check_output(cmd, shell=True).decode().strip()

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = ''
    while True:
        line = proc.stdout.readline().decode('utf-8')
        output += line
        if not line:
            break
        print(line.rstrip())



def git_clone():
    os.chdir(sys.path[0])
    commands = ['git rev-parse HEAD']

    if os.path.isdir('./http_server'):
        print('Repository exists, pulling changes')
        os.chdir('./http_server')
        commands.insert(0, 'git pull')
    else:
        commands.insert(0, 'git clone -b main --single-branch https://github.com/sawasy/http_server')

    for cmd in commands:
        output = run_command(cmd, output=True)
        if 'clone' in cmd:
            os.chdir('./http_server')

    os.chdir(sys.path[0])
    return output


def init_minikube(delete):
    if delete:
        run_command('minikube delete')
    run_command('minikube start --nodes 3')


def rollback():
    print("Starting rollback ... ")
    run_command("minikube kubectl -- --context=minikube rollout undo deployment/{app}".format(app=app_name))


def apply_k8s(obj, kind):
    print("Starting deploy for {app}".format(app=app_name))
    # with open("{s}.json".format(s=service_name), "w") as f:
    #     f.write(json.dumps(deployment_obj, indent=4))
    cmd = """cat << EOF | minikube kubectl -- --context=minikube apply --record=true -f -
            {deployment}\nEOF""".format(
            deployment=json.dumps(obj, indent=4))
    run_command(cmd)

    if kind == 'deployment':
        sts = run_command(
            "minikube kubectl -- --context=minikube rollout status deployment/{app}".format(app=app_name)
        )

def docker_build(image_name):
    run_command('docker build --pull -t {image_name} .'.format(image_name=image_name))


def load_image(image_name):
    run_command('minikube image load {image_name}'.format(image_name=image_name))


def deploy(image_name):
    deployment_obj, service_obj = k8s_manifests.get_manifests(app_name, image_name)
    apply_k8s(deployment_obj, 'deployment')
    apply_k8s(service_obj, 'service')


def main():
    repo_hash = git_clone()
    image_name = "{app_name}:{repo_hash}".format(app_name=app_name, repo_hash=repo_hash)
    docker_build(image_name)
    init_minikube(delete_cluster)
    load_image(image_name)
    deploy(image_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='generate-service.py',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100,
                                                                                         width=200))
    parser.add_argument('-app_name', "-n", type=str, required=False, default=None, help='Name of the application')
    parser.add_argument('-delete_cluster', "-del", type=bool, required=False, default=False, help='Delete existing minikube')

    args = parser.parse_args()
    app_name = args.app_name
    delete_cluster = args.delete_cluster

    if app_name is None or app_name == "":
        print("Please provide the application name")
        exit(0)

    main()
