
manually

```bash
GITEA_INT_URL="http://gitea.gitea.svc:3000/"
GITEA_REPO="opentlc-mgr/insurance-claim-processing-mirror/"
GITEA_BRANCH="feature/minio-in-gitops/"
GITEA_APP_PATH="bootstrap/applications/shared-minio-app.yaml"

CMD=" oc apply -f ${GITEA_INT_URL}${GITEA_REPO}raw/branch/${GITEA_BRANCH}${GITEA_APP_PATH}"

# https://gitea.apps.cluster-rvl84.sandbox483.opentlc.com/opentlc-mgr/insurance-claim-processing-mirror/raw/branch/feature/minio-in-gitops/bootstrap/applications/shared-minio-app.yaml
echo "http://gitea.gitea.svc:3000/opentlc-mgr/insurance-claim-processing-mirror/raw/branch/feature/minio-in-gitops/bootstrap/applications/shared-minio-app.yaml"
echo ${CMD}

```
