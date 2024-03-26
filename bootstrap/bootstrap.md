## Deploy Manually

```bash
GITEA_INT_URL="http://gitea.gitea.svc:3000/"
GITEA_REPO="opentlc-mgr/insurance-claim-processing-mirror/"
GITEA_BRANCH="dev/"
GITEA_APP_PATH="bootstrap/applications/ic-shared-minio-app.yaml"

CMD="oc apply -f ${GITEA_INT_URL}${GITEA_REPO}raw/branch/${GITEA_BRANCH}${GITEA_APP_PATH}"

echo ${CMD}

oc apply -f ./bootstrap/applicationset/applicationset-bootstrap.yaml
```
