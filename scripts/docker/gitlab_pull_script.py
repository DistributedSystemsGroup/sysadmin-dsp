import requests
import zipfile
import io
import json
import os
import traceback

GITLAB_TOKEN=""
token_header = {'PRIVATE-TOKEN': GITLAB_TOKEN}

GROUP = 'zoe-apps'
ZAPP_STORE_PATH = '/mnt/cephfs/zoe-apps/'

def get_projects(group):
    prj_list = []
    r = requests.get("http://gitlab.eurecom.fr/api/v4/groups/{}/projects".format(group), headers=token_header)
    for project in r.json():
        prj_list.append((project['name'], project['id']))
    return prj_list


def get_images_from_zapp(zapp):
    images = []
    for s in zapp['services']:
        images.append(s['image'])
    return images


def pull_images(images):
    for image in images:
        print(image)
        os.system("docker -H 192.168.47.5:2380 pull {}".format(image))


def main(project_name, project):
    r = requests.get("http://gitlab.eurecom.fr/api/v4/projects/{}/pipelines?status=success".format(project), headers=token_header)

    pipelines = r.json()
    if len(pipelines) > 0:
        latest_pipeline_run = pipelines[0]['id']
    else:
        return

    r = requests.get("http://gitlab.eurecom.fr/api/v4/projects/{}/pipelines/{}/jobs?scope=success".format(project, latest_pipeline_run), headers=token_header)
    jobs = r.json()
    if len(jobs) == 0:
        return

    for good_job in jobs:
        r = requests.get("http://gitlab.eurecom.fr/api/v4/projects/{}/jobs/{}/artifacts".format(project, good_job['id']), headers=token_header)
        artifact = r.content
        f_obj = io.BytesIO(artifact)
        zp = zipfile.ZipFile(f_obj)
        for member in zp.namelist():
            if member[-5:] != ".json" or member == "manifest.json":
                continue

            zapp_bytes = zp.read(member)
            zapp = json.loads(zapp_bytes.decode('utf-8'))
            images = get_images_from_zapp(zapp)
            pull_images(images)
            print(project_name + "/" + member)
            if os.path.exists(os.path.join(ZAPP_STORE_PATH, project_name)):
                open(os.path.join(ZAPP_STORE_PATH, project_name, member), 'wb').write(zapp_bytes)


if __name__ == "__main__":
    for p in get_projects(GROUP):
        try:
            main(*p)
        except Exception as e:
            traceback.print_exc()
            continue


