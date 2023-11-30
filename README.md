# Insurance Claim Processing

## Instructions Development

### Requirements

- Podman or Docker

### Development

- Add/Modify/Delete content in [instructions/content/modules/ROOT](instructions/content/modules/ROOT).
- Navigation is handled in `nav.adoc`.
- Content pages are in the `pages` folder.
- To build the site, from the root of the repo, run `./instructions/utilities/lab-build`.
- To serve the site for previewing, from the root of the repo, run `instructions/utilities/lab-serve`.
- The site will be visible at [http://localhost:8443/](http://localhost:8443/)
- When finished, you can stop serving the site by running from the root of the repo `instructions/utilities/lab-stop`.

## Application Development

### Requirements

- Python 3.11
- Nodejs > 18
- An existing instance of Hugging Face TGI with a loaded model available at `INFERENCE_SERVER_URL`. This application is based on Mistral-TB Prompt format. You will need to modify this format if you are using a different model.

### Installation

Run `npm install` from the main folder.

If you want to install packages manually:

- In the `frontend` folder, install the node modules with `npm install`.
- In the `backend` folder, create a venv and install packages with the provided Pipfile/Pipfile.lock files.
- In the `backend` folder, create the file `.env` base on the example `.env.example` and enter the configuration for the Inference server.

### Develop

From the main folder, launch `npm run dev`. This will launch both backend and frontend.

- Frontend is accessible at `http://localhost:9000`
- Backend is accessible at `http://localhost:5000`, with Swagger API doc at `http://localhost:5000/docs`
