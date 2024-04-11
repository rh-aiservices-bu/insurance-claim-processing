import yaml
from argparse import ArgumentParser
from pathlib import Path
import json

def main():
    arguments = _read_arguments()
    user_count = arguments.user_count
    generate_resource_manifest(user_count)


def _read_arguments():
    parser = ArgumentParser()
    parser.add_argument('--user_count', type=int)
    arguments = parser.parse_args()
    return arguments

def get_resource_functions():
    return {
        "project": _get_project_resource,
        "project_role_binding": _get_role_binding_resource,
        "minio": _get_minio_resource,
        "ds_connections": _get_ds_connections,
        "pipeline": _get_pipelines_definition_resource,
        "workbench_pvc": _get_workbench_pvc_resource,
        "workbench": _get_workbench_resource,
        "git_clone_job": _get_git_clone_job,
        "pipeline_secret": _get_pipeline_secret,
    }

def generate_resource_manifest(user_count):
    resources = get_resource_functions()
    for resource_name, func in resources.items():
      sum_user_res = []
      for index in range(1, user_count+1):
          sum_user_res.append(func(f'user{index}-auto', f'user{index}'))
      
      manifests = [
          yaml.dump(resource) if type(resource) is dict else resource for resource in sum_user_res 
      ]

      Path("resources").mkdir(exist_ok=True)

      overall_manifest = ''
      for manifest in manifests:
          overall_manifest += manifest
          overall_manifest += '---\n'
      with open(f"resources/{resource_name}.yaml", 'w') as outputfile:
          outputfile.write(overall_manifest)
      print(f'Wrote manifest {resource_name}')


def _get_minio_resource(namespace, user):
    resource = """
apiVersion: v1
kind: Service
metadata:
  labels:
    app: minio
    app.kubernetes.io/component: minio
    app.kubernetes.io/instance: minio
    app.kubernetes.io/name: minio
    app.kubernetes.io/part-of: minio
    component: minio
  name: minio
  namespace: {namespace}
spec:
  ports:
  - name: api
    port: 9000
    targetPort: api
  - name: console
    port: 9090
    targetPort: 9090
  selector:
    app: minio
    app.kubernetes.io/component: minio
    app.kubernetes.io/instance: minio
    app.kubernetes.io/name: minio
    app.kubernetes.io/part-of: minio
    component: minio
  sessionAffinity: None
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  labels:
    app: minio
    app.kubernetes.io/component: minio
    app.kubernetes.io/instance: minio
    app.kubernetes.io/name: minio
    app.kubernetes.io/part-of: minio
    component: minio
  name: minio
  namespace: {namespace}
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: minio
    app.kubernetes.io/component: minio
    app.kubernetes.io/instance: minio
    app.kubernetes.io/name: minio
    app.kubernetes.io/part-of: minio
    component: minio
  name: minio
  namespace: {namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
      app.kubernetes.io/component: minio
      app.kubernetes.io/instance: minio
      app.kubernetes.io/name: minio
      app.kubernetes.io/part-of: minio
      component: minio
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: minio
        app.kubernetes.io/component: minio
        app.kubernetes.io/instance: minio
        app.kubernetes.io/name: minio
        app.kubernetes.io/part-of: minio
        component: minio
    spec:
      containers:
      - args:
        - minio server /data --console-address :9090
        command:
        - /bin/bash
        - -c
        envFrom:
        - secretRef:
            name: minio-root-user
        image: quay.io/minio/minio:latest
        name: minio
        ports:
        - containerPort: 9000
          name: api
          protocol: TCP
        - containerPort: 9090
          name: console
          protocol: TCP
        resources:
          limits:
            cpu: "2"
            memory: 2Gi
          requests:
            cpu: 200m
            memory: 1Gi
        volumeMounts:
        - mountPath: /data
          name: minio
      volumes:
      - name: minio
        persistentVolumeClaim:
          claimName: minio
      - emptyDir: {}
        name: empty
---
apiVersion: batch/v1
kind: Job
metadata:
  labels:
    app.kubernetes.io/component: minio
    app.kubernetes.io/instance: minio
    app.kubernetes.io/name: minio
    app.kubernetes.io/part-of: minio
    component: minio
  name: create-minio-buckets
  namespace: {namespace}
spec:
  selector: {}
  template:
    metadata:
      labels:
        app.kubernetes.io/component: minio
        app.kubernetes.io/instance: minio
        app.kubernetes.io/name: minio
        app.kubernetes.io/part-of: minio
        component: minio
    spec:
      containers:
      - args:
        - -ec
        - |-
          oc get secret minio-root-user
          env | grep MINIO
          cat << 'EOF' | python3
          import boto3, os

          s3 = boto3.client("s3",
                            endpoint_url="http://minio:9000",
                            aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
                            aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"))
          bucket = 'pipeline-artifacts'
          print('creating pipeline-artifacts bucket')
          if bucket not in [bu["Name"] for bu in s3.list_buckets()["Buckets"]]:
            s3.create_bucket(Bucket=bucket)
          EOF
        command:
        - /bin/bash
        envFrom:
        - secretRef:
            name: minio-root-user
        image: quay.io/rlundber/sds-small:1.8
        imagePullPolicy: IfNotPresent
        name: create-buckets
      initContainers:
      - args:
        - -ec
        - |-
          echo -n 'Waiting for minio root user secret'
          while ! oc get secret minio-root-user 2>/dev/null | grep -qF minio-root-user; do
          echo -n .
          sleep 5
          done; echo

          echo -n 'Waiting for minio deployment'
          while ! oc get deployment minio 2>/dev/null | grep -qF minio; do
            echo -n .
            sleep 5
          done; echo
          oc wait --for=condition=available --timeout=60s deployment/minio
          sleep 10
        command:
        - /bin/bash
        image: quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:95b359257a7716b5f8d3a672081a84600218d8f58ca720f46229f7bb893af2ab
        imagePullPolicy: IfNotPresent
        name: wait-for-minio
      restartPolicy: Never
      serviceAccount: demo-setup
      serviceAccountName: demo-setup
---
apiVersion: batch/v1
kind: Job
metadata:
  labels:
    app.kubernetes.io/component: minio
    app.kubernetes.io/instance: minio
    app.kubernetes.io/name: minio
    app.kubernetes.io/part-of: minio
    component: minio
  name: create-minio-root-user
  namespace: {namespace}
spec:
  backoffLimit: 4
  template:
    metadata:
      labels:
        app.kubernetes.io/component: minio
        app.kubernetes.io/instance: minio
        app.kubernetes.io/name: minio
        app.kubernetes.io/part-of: minio
        component: minio
    spec:
      containers:
      - args:
        - -ec
        - |-
          if [ -n "$(oc get secret minio-root-user -oname 2>/dev/null)" ]; then
            echo "Secret already exists. Skipping." >&2
            exit 0
          fi
          genpass() {
              < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c"${1:-32}"
          }
          id=$(genpass 16)
          secret=$(genpass)
          cat << EOF | oc apply -f-
          apiVersion: v1
          kind: Secret
          metadata:
            name: minio-root-user
          type: Opaque
          stringData:
            MINIO_ROOT_USER: ${id}
            MINIO_ROOT_PASSWORD: ${secret}
          EOF
        command:
        - /bin/bash
        image: quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:95b359257a7716b5f8d3a672081a84600218d8f58ca720f46229f7bb893af2ab
        imagePullPolicy: IfNotPresent
        name: create-minio-root-user
      restartPolicy: Never
      serviceAccount: demo-setup
      serviceAccountName: demo-setup
---
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  labels:
    app: minio
    app.kubernetes.io/component: minio
    app.kubernetes.io/instance: minio
    app.kubernetes.io/name: minio
    app.kubernetes.io/part-of: minio
    component: minio
  name: minio-console
  namespace: {namespace}
spec:
  port:
    targetPort: console
  tls:
    insecureEdgeTerminationPolicy: Redirect
    termination: edge
  to:
    kind: Service
    name: minio
    weight: 100
  wildcardPolicy: None
---
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  labels:
    app: minio
    app.kubernetes.io/component: minio
    app.kubernetes.io/instance: minio
    app.kubernetes.io/name: minio
    app.kubernetes.io/part-of: minio
    component: minio
  name: minio-s3
  namespace: {namespace}
spec:
  port:
    targetPort: api
  tls:
    insecureEdgeTerminationPolicy: Redirect
    termination: edge
  to:
    kind: Service
    name: minio
    weight: 100
  wildcardPolicy: None
""".replace("{user}", user).replace("{namespace}", namespace)
    return resource


def _get_ds_connections(namespace, user):
    ds_connections = """apiVersion: batch/v1
kind: Job
metadata:
  name: create-ds-connections
  namespace: {namespace}
spec:
  selector: {}
  template:
    spec:
      containers:
      - args:
        - -ec
        - |-
          echo -n "Waiting for minio-root-user to exist"
          while [ -z "$(oc get secret -n ic-shared-minio minio-root-user -oname 2>/dev/null)" ]; do
            echo -n '.'
            sleep 1
          done; echo
          id=$(oc get secret -n ic-shared-minio minio-root-user -ogo-template='{{.data.MINIO_ROOT_USER|base64decode}}')
          secret=$(oc get secret -n ic-shared-minio minio-root-user -ogo-template='{{.data.MINIO_ROOT_PASSWORD|base64decode}}')
          echo "Minio Console : https://$(oc get route -n ic-shared-minio minio-console -ojsonpath='{.status.ingress[0].host}')/ "
          echo "Minio user: ${id}"
          echo "Minio pass: ${secret}"
          echo "Internal service url: http://minio.ic-shared-minio.svc.cluster.local:9000/"
          cat << EOF | oc apply -f-
          apiVersion: v1
          kind: Secret
          metadata:
            name: aws-connection-shared-minio---pipelines
            labels:
              opendatahub.io/dashboard: "true"
              opendatahub.io/managed: "true"
            annotations:
              opendatahub.io/connection-type: s3
              openshift.io/display-name: Shared Minio - pipelines
          type: Opaque
          stringData:
            AWS_ACCESS_KEY_ID: ${id}
            AWS_SECRET_ACCESS_KEY: ${secret}
            AWS_DEFAULT_REGION: us
            AWS_S3_ENDPOINT: http://minio.ic-shared-minio.svc:9000
            AWS_S3_BUCKET: {user}
          EOF
        command:
        - /bin/bash
        image: quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:95b359257a7716b5f8d3a672081a84600218d8f58ca720f46229f7bb893af2ab
        imagePullPolicy: IfNotPresent
        name: create-ds-connections
      restartPolicy: Never
      serviceAccount: demo-setup
      serviceAccountName: demo-setup
""".replace("{namespace}", namespace).replace("{user}", user)

    return ds_connections


def _get_project_resource(namespace, user):
    project_resource = {
        'kind': 'Project',
        'apiVersion': 'project.openshift.io/v1',
        'metadata': {
            'name': namespace,
            'labels': {
                'kubernetes.io/metadata.name': namespace,
                'modelmesh-enabled': 'true',
                'opendatahub.io/dashboard': 'true',
            },
            'annotations': {
                'openshift.io/description': '',
                'openshift.io/display-name': namespace,
            }
        },
        'spec': {
            'finalizers': ['kubernetes']
        }
    }
    return project_resource


def _get_role_binding_resource(namespace, user):
    notebook_name = "my-workbench"
    role_binding_resource = """apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: admin
  namespace: {namespace}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: admin
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: {user}
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: demo-setup
  namespace: {namespace}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: demo-setup-edit
  namespace: {namespace}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: edit
subjects:
- kind: ServiceAccount
  name: demo-setup
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: demo-setup-route-reader-binding-{namespace}
subjects:
- kind: ServiceAccount
  name: demo-setup
  namespace: {namespace}
roleRef:
  kind: ClusterRole
  name: route-reader
  apiGroup: rbac.authorization.k8s.io
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: elyra-pipelines-{notebook_name}
  namespace: {namespace}
  labels:
    opendatahub.io/dashboard: 'true'
subjects:
  - kind: ServiceAccount
    name: {notebook_name}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ds-pipeline-user-access-pipelines-definition
""".replace("{namespace}", namespace).replace("{user}", user).replace("{notebook_name}", notebook_name)
    
    return role_binding_resource


def _get_pipelines_definition_resource(namespace, user):
    pipelines_definition_resource = {
        'apiVersion': 'datasciencepipelinesapplications.opendatahub.io/v1alpha1',
        'kind': 'DataSciencePipelinesApplication',
        'metadata':{
            'finalizers':['datasciencepipelinesapplications.opendatahub.io/finalizer'],
            'name': 'pipelines-definition',
            'namespace': namespace,
        },
        'spec':{
            'apiServer':{
                'stripEOF': True,
                'dbConfigConMaxLifetimeSec': 120,
                'applyTektonCustomResource': True,
                'deploy': True,
                'enableSamplePipeline': False,
                'autoUpdatePipelineDefaultVersion': True,
                'archiveLogs': False,
                'terminateStatus': 'Cancelled',
                'enableOauth': True,
                'trackArtifacts': True,
                'collectMetrics': True,
                'injectDefaultScript': True,
            },
            'database':{
                'mariaDB':{
                    'deploy': True,
                    'pipelineDBName': 'mlpipeline',
                    'pvcSize': '10Gi',
                    'username': 'mlpipeline',
                }
            },
            'objectStorage':{
                'externalStorage':{
                    'bucket': f'{user}',
                    'host': f'minio.ic-shared-minio.svc.cluster.local:9000',
                    'port': '',
                    's3CredentialsSecret':{
                        'accessKey': 'AWS_ACCESS_KEY_ID',
                        'secretKey': 'AWS_SECRET_ACCESS_KEY',
                        'secretName': 'aws-connection-shared-minio---pipelines',
                    },
                    'scheme': 'http',
                    'secure': False,
                }
            },
            'persistenceAgent':{
                'deploy': True,
                'numWorkers': 2
            },
            'scheduledWorkflow':{
                'cronScheduleTimezone': 'UTC',
                'deploy': True,
            }
        }
    }
    return pipelines_definition_resource

def _get_workbench_pvc_resource(namespace, user):
    notebook_name = "my-workbench"
    pvc = """kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  annotations:
    openshift.io/description: ''
    openshift.io/display-name: My Workbench
    volume.beta.kubernetes.io/storage-provisioner: openshift-storage.rbd.csi.ceph.com
    volume.kubernetes.io/storage-provisioner: openshift-storage.rbd.csi.ceph.com
  name: {notebook_name}
  namespace: {namespace}
  finalizers:
    - kubernetes.io/pvc-protection
  labels:
    opendatahub.io/dashboard: 'true'
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: ocs-storagecluster-ceph-rbd
  volumeMode: Filesystem
""".replace("{notebook_name}", notebook_name).replace("{namespace}", namespace)
    return pvc

def _get_workbench_resource(namespace, user):
    notebook_name = "my-workbench"
    image = "ic-workbench:2.0"
    workbench_job = """apiVersion: batch/v1
kind: Job
metadata:
  name: create-workbench
  namespace: {namespace}
spec:
  selector: {}
  template:
    spec:
      containers:
      - args:
        - -ec
        - |-
          DASHBOARD_ROUTE=https://$(oc get route rhods-dashboard -n redhat-ods-applications -o jsonpath='{.spec.host}')

          cat << EOF | oc apply -f-
          apiVersion: kubeflow.org/v1
          kind: Notebook
          metadata:
            annotations:
              notebooks.opendatahub.io/inject-oauth: 'true'
              opendatahub.io/image-display-name: CUSTOM - Insurance Claim Processing Lab Workbench
              notebooks.opendatahub.io/oauth-logout-url: >-
                ${DASHBOARD_ROUTE}/projects/{namespace}?notebookLogout={notebook_name}
              opendatahub.io/accelerator-name: ''
              openshift.io/description: ''
              openshift.io/display-name: My Workbench
              notebooks.opendatahub.io/last-image-selection: '{image}'
              notebooks.opendatahub.io/last-size-selection: Standard
              opendatahub.io/username: {user}
            name: {notebook_name}
            namespace: {namespace}
            labels:
              app: {notebook_name}
              opendatahub.io/dashboard: 'true'
              opendatahub.io/odh-managed: 'true'
              opendatahub.io/user: {user}
          spec:
            template:
              spec:
                affinity: {}
                containers:
                  - resources:
                      limits:
                        cpu: '2'
                        memory: 8Gi
                      requests:
                        cpu: '1'
                        memory: 6Gi
                    readinessProbe:
                      failureThreshold: 3
                      httpGet:
                        path: /notebook/{namespace}/{notebook_name}/api
                        port: notebook-port
                        scheme: HTTP
                      initialDelaySeconds: 10
                      periodSeconds: 5
                      successThreshold: 1
                      timeoutSeconds: 1
                    name: {notebook_name}
                    livenessProbe:
                      failureThreshold: 3
                      httpGet:
                        path: /notebook/{namespace}/{notebook_name}/api
                        port: notebook-port
                        scheme: HTTP
                      initialDelaySeconds: 10
                      periodSeconds: 5
                      successThreshold: 1
                      timeoutSeconds: 1
                    env:
                      - name: NOTEBOOK_ARGS
                        value: |-
                          --ServerApp.port=8888
                                            --ServerApp.token=''
                                            --ServerApp.password=''
                                            --ServerApp.base_url=/notebook/{namespace}/{notebook_name}
                                            --ServerApp.quit_button=False
                                            --ServerApp.tornado_settings={"user":"{user}","hub_host":"${DASHBOARD_ROUTE}","hub_prefix":"/projects/{namespace}"}
                      - name: JUPYTER_IMAGE
                        value: >-
                          image-registry.openshift-image-registry.svc:5000/redhat-ods-applications/{image}
                    ports:
                      - containerPort: 8888
                        name: notebook-port
                        protocol: TCP
                    imagePullPolicy: Always
                    volumeMounts:
                      - mountPath: /opt/app-root/src
                        name: {notebook_name}
                      - mountPath: /opt/app-root/runtimes
                        name: elyra-dsp-details
                      - mountPath: /dev/shm
                        name: shm
                    image: >-
                      image-registry.openshift-image-registry.svc:5000/redhat-ods-applications/{image}
                    workingDir: /opt/app-root/src
                  - resources:
                      limits:
                        cpu: 100m
                        memory: 64Mi
                      requests:
                        cpu: 100m
                        memory: 64Mi
                    readinessProbe:
                      failureThreshold: 3
                      httpGet:
                        path: /oauth/healthz
                        port: oauth-proxy
                        scheme: HTTPS
                      initialDelaySeconds: 5
                      periodSeconds: 5
                      successThreshold: 1
                      timeoutSeconds: 1
                    name: oauth-proxy
                    livenessProbe:
                      failureThreshold: 3
                      httpGet:
                        path: /oauth/healthz
                        port: oauth-proxy
                        scheme: HTTPS
                      initialDelaySeconds: 30
                      periodSeconds: 5
                      successThreshold: 1
                      timeoutSeconds: 1
                    env:
                      - name: NAMESPACE
                        valueFrom:
                          fieldRef:
                            fieldPath: metadata.namespace
                    ports:
                      - containerPort: 8443
                        name: oauth-proxy
                        protocol: TCP
                    imagePullPolicy: Always
                    volumeMounts:
                      - mountPath: /etc/oauth/config
                        name: oauth-config
                      - mountPath: /etc/tls/private
                        name: tls-certificates
                    image: >-
                      registry.redhat.io/openshift4/ose-oauth-proxy@sha256:4bef31eb993feb6f1096b51b4876c65a6fb1f4401fee97fa4f4542b6b7c9bc46
                    args:
                      - '--provider=openshift'
                      - '--https-address=:8443'
                      - '--http-address='
                      - '--openshift-service-account={notebook_name}'
                      - '--cookie-secret-file=/etc/oauth/config/cookie_secret'
                      - '--cookie-expire=24h0m0s'
                      - '--tls-cert=/etc/tls/private/tls.crt'
                      - '--tls-key=/etc/tls/private/tls.key'
                      - '--upstream=http://localhost:8888'
                      - '--upstream-ca=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
                      - '--email-domain=*'
                      - '--skip-provider-button'
                      - >-
                        --openshift-sar={"verb":"get","resource":"notebooks","resourceAPIGroup":"kubeflow.org","resourceName":"{notebook_name}","namespace":"$(NAMESPACE)"}
                      - >-
                        --logout-url=${DASHBOARD_ROUTE}/projects/{namespace}?notebookLogout={notebook_name}
                enableServiceLinks: false
                serviceAccountName: {notebook_name}
                tolerations:
                  - effect: NoSchedule
                    key: notebooksonly
                    operator: Exists
                volumes:
                  - name: {notebook_name}
                    persistentVolumeClaim:
                      claimName: {notebook_name}
                  - name: elyra-dsp-details
                    secret:
                      secretName: ds-pipeline-config
                  - emptyDir:
                      medium: Memory
                    name: shm
                  - name: oauth-config
                    secret:
                      defaultMode: 420
                      secretName: {notebook_name}-oauth-config
                  - name: tls-certificates
                    secret:
                      defaultMode: 420
                      secretName: {notebook_name}-tls
            readyReplicas: 1
          EOF
        command:
        - /bin/bash
        image: quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:95b359257a7716b5f8d3a672081a84600218d8f58ca720f46229f7bb893af2ab
        imagePullPolicy: IfNotPresent
        name: create-workbench
      restartPolicy: Never
      serviceAccount: demo-setup
      serviceAccountName: demo-setup
""".replace("{notebook_name}", notebook_name).replace("{user}", user).replace("{namespace}", namespace).replace("{image}", image)
    
    return workbench_job

def _get_git_clone_job(namespace, user):
    notebook_name = "my-workbench"
    clone_job = """apiVersion: batch/v1
kind: Job
metadata:
  name: clone-repo
  namespace: {namespace}
spec:
  backoffLimit: 4
  template:
    spec:
      serviceAccount: demo-setup
      serviceAccountName: demo-setup
      initContainers:
      - name: wait-for-workbench
        image: image-registry.openshift-image-registry.svc:5000/openshift/tools:latest
        imagePullPolicy: IfNotPresent
        command: ["/bin/bash"]
        args:
        - -ec
        - |-
          echo -n "Waiting for workbench pod in {namespace} namespace"
          while [ -z "$(oc get pods -n {namespace} -l app={notebook_name} -o custom-columns=STATUS:.status.phase --no-headers | grep Running 2>/dev/null)" ]; do
              echo -n '.'
              sleep 1
          done
          echo "Workbench pod is running in {namespace} namespace"
      containers:
      - name: git-clone
        image: image-registry.openshift-image-registry.svc:5000/redhat-ods-applications/s2i-generic-data-science-notebook:1.2
        imagePullPolicy: IfNotPresent
        command: ["/bin/bash"]
        args:
        - -ec
        - |-
          pod_name=$(oc get pods --selector=app={notebook_name} -o jsonpath='{.items[0].metadata.name}') && oc exec $pod_name -- git clone https://github.com/rh-aiservices-bu/insurance-claim-processing
      restartPolicy: Never
""".replace("{namespace}", namespace).replace("{notebook_name}", notebook_name)
    return clone_job

def _get_pipeline_secret(namespace, user):
    engine = "Tekton" #'Tekton', // or 'Argo' on v2

    create_secret_job = """apiVersion: batch/v1
kind: Job
metadata:
  name: create-pipeline-secret
  namespace: {namespace}
spec:
  selector: {}
  template:
    spec:
      containers:
      - args:
        - -ec
        - |-
          echo -n 'Waiting for ds-pipeline-pipelines-definition route'
          while ! oc get route ds-pipeline-pipelines-definition 2>/dev/null; do
            echo -n .
            sleep 5
          done; echo

          MINIO_ROOT_USER=$(oc get secret minio-root-user -n ic-shared-minio -o template --template '{{.data.MINIO_ROOT_USER|base64decode}}')
          MINIO_ROOT_PASSWORD=$(oc get secret minio-root-user -n ic-shared-minio -o template --template '{{.data.MINIO_ROOT_PASSWORD|base64decode}}')
          MINIO_HOST=https://$(oc get route minio-s3 -n ic-shared-minio -o template --template '{{.spec.host}}')
          DASHBOARD_ROUTE=https://$(oc get route rhods-dashboard -n redhat-ods-applications -o jsonpath='{.spec.host}')
          PIPELINE_ROUTE=https://$(oc get route ds-pipeline-pipelines-definition -o jsonpath='{.spec.host}')

          cat << EOF | oc apply -f-
          apiVersion: v1
          kind: Secret
          metadata:
            name: ds-pipeline-config
            namespace: {namespace}
          stringData:
            odh_dsp.json: '{"display_name": "Data Science Pipeline", "metadata": {"tags": [],
              "display_name": "Data Science Pipeline", "engine": {engine}, "auth_type": "KUBERNETES_SERVICE_ACCOUNT_TOKEN",
              "api_endpoint": "${PIPELINE_ROUTE}",
              "public_api_endpoint": "${DASHBOARD_ROUTE}/pipelineRuns/{namespace}/pipelineRun/view/",
              "cos_auth_type": "KUBERNETES_SECRET", "cos_secret": "aws-connection-shared-minio---pipelines",
              "cos_endpoint": "${MINIO_HOST}", "cos_bucket": "{user}",
              "cos_username": "${MINIO_ROOT_USER}", "cos_password": "${MINIO_ROOT_PASSWORD}",
              "runtime_type": "KUBEFLOW_PIPELINES"}, "schema_name": "kfp"}'
          type: Opaque
          EOF
        command:
        - /bin/bash
        image: quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:95b359257a7716b5f8d3a672081a84600218d8f58ca720f46229f7bb893af2ab
        imagePullPolicy: IfNotPresent
        name: create-ds-connections
      restartPolicy: Never
      serviceAccount: demo-setup
      serviceAccountName: demo-setup
""".replace("{namespace}", namespace).replace("{engine}", engine).replace("{user}", user)
    return create_secret_job

if __name__ == '__main__':
    main()