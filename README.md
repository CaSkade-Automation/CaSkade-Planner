<img align="left" height="100px" src="https://avatars.githubusercontent.com/u/149593817?s=200&v=4">
<h1>CaSkade Planner - Capability-based Process Planning using SMT</h1>

CaSkade-Planner is an automated planning approach to derive process sequences that consist of provided capabilities for one or more required capabilities. It makes use of the [CaSk ontology](https://github.com/CaSkade-Automation/CaSk). There are different ways to install and use this tool:

1. Install and run locally
2. Run as a docker container
3. Integrate into your own Python scripts

You can find detailed instructions to every option in the sections below.

## Local Installation
Make sure that you have [Poetry](https://python-poetry.org/) installed. Clone this repository, open a terminal inside the repo's root folder and install everything using `poetry install`. Afterwards you can use CaSkade-Planner according to the instructions below.

### CLI
CaSkade-Planner provides a command-line interface with two main commands. You can always open the help with the `--help` option.

#### Plan from local ontology file
To plan from a local ontology file, use: `poetry run caskade-planner-cli plan-from-file`

```
Arguments:
  ONTOLOGY_FILE           Path to your ontology that is used for generating the
                          planning problem  [required]
  REQUIRED_CAPABILITY_IRI IRI of the required capability to plan for  [required]

Options:
  -mh, --max-happenings INTEGER  Maximum number of happenings to consider
                                 [default: 20]
  -problem, --problem-file TEXT  Path to where the generated problem will be
                                 stored
  -model, --model-file TEXT      Path to where the model file will be stored
                                 after solving
  -plan, --plan-file TEXT        Path to where the plan file will be stored
                                 after solving and transformation
  --help                         Show this message and exit.
```

**Example:**
```bash
poetry run caskade-planner-cli plan-from-file my-ontology.ttl http://example.org/capabilities#RequiredCapability1
```

#### Plan from SPARQL endpoint
To plan directly from a SPARQL endpoint, use: `poetry run caskade-planner-cli plan-from-endpoint`

```
Arguments:
  ENDPOINT_URL            URL of the SPARQL endpoint  [required]
  REQUIRED_CAPABILITY_IRI IRI of the required capability to plan for  [required]

Options:
  -mh, --max-happenings INTEGER  Maximum number of happenings to consider
                                 [default: 20]
  -problem, --problem-file TEXT  Path to where the generated problem will be
                                 stored
  -model, --model-file TEXT      Path to where the model file will be stored
                                 after solving
  -plan, --plan-file TEXT        Path to where the plan file will be stored
                                 after solving and transformation
  --help                         Show this message and exit.
```

**Example:**
```bash
poetry run caskade-planner-cli plan-from-endpoint http://localhost:7200/repositories/test-repo http://example.org/capabilities#RequiredCapability1
```

The `plan-from-endpoint` command outputs the result as JSON to stdout, making it easy to integrate with other tools.

### REST-API
If you want to use CaSkade-Planner as a standalone planning service to be used by other software components, you can integrate it as a REST API.
After cloning and installing the project, start the REST API by calling `poetry run caskade-planner-api`. The planning API runs on port 5000.

#### Endpoints

- `GET /ping` - Health check endpoint (returns 204 No Content)
- `POST /plan` - Main planning endpoint

#### Planning Request
Send an HTTP POST request to `<API-Address>:5000/plan` with a JSON body:

```json
{
  "mode": "file" | "sparql-endpoint",
  "requiredCapabilityIri": "<IRI of the required capability>",
  "maxHappenings": 5,  // optional, defaults to 5
  "endpointUrl": "<SPARQL endpoint URL>"  // only for mode="sparql-endpoint"
}
```

For `mode="file"`, you need to upload the ontology file as multipart/form-data with the key `"ontology-file"`.

#### Response Format
Both CLI and REST API return results in JSON format:

```json
{
  "timeCreated": "2024-01-01T12:00:00Z",
  "resultType": "sat" | "unsat",
  "plan": {  // only if resultType="sat"
    "plan_steps": [...],
    "plan_length": 5,
    "total_duration": 120
  },
  "unsatCore": [...]  // only if resultType="unsat"
}
```

## Docker

CaSkade-Planner is available as a Docker image on Docker Hub at `aljoshakoecher/caskade-planner`. The image supports multiple modes of operation through a flexible entrypoint system.

### Quick Start

#### Pull the latest image:
```bash
docker pull aljoshakoecher/caskade-planner:latest
```

#### Run REST API:
```bash
docker run -p 5000:5000 aljoshakoecher/caskade-planner:latest rest
```

#### Run CLI commands:
```bash
# Plan from file
docker run -it --rm -v "$(pwd):/data" \
  aljoshakoecher/caskade-planner:latest \
  plan-from-file /data/my-ontology.ttl http://example.org/capabilities#RequiredCapability1

# Plan from endpoint
docker run -it --rm \
  aljoshakoecher/caskade-planner:latest \
  plan-from-endpoint http://host.docker.internal:7200/repositories/test-repo http://example.org/capabilities#RequiredCapability1
```

### Available Commands

The Docker image supports the following commands through its entrypoint:

#### `rest` - Start REST API Server
```bash
docker run -p 5000:5000 aljoshakoecher/caskade-planner:latest rest
```
Starts the REST API server on port 5000. The API will be accessible at `http://localhost:5000`.

#### `plan-from-file` - Direct File Planning
```bash
docker run -it --rm -v "$(pwd):/data" \
  aljoshakoecher/caskade-planner:latest \
  plan-from-file /data/ontology.ttl http://capability.iri [OPTIONS]
```

Available options:
- `--max-happenings INTEGER` (default: 20)
- `--problem-file TEXT`
- `--model-file TEXT`
- `--plan-file TEXT`

#### `plan-from-endpoint` - Direct Endpoint Planning
```bash
docker run -it --rm \
  aljoshakoecher/caskade-planner:latest \
  plan-from-endpoint http://endpoint-url http://capability.iri [OPTIONS]
```

#### `cli` - Full CLI Access
```bash
docker run -it --rm -v "$(pwd):/data" \
  aljoshakoecher/caskade-planner:latest \
  cli plan-from-file /data/ontology.ttl http://capability.iri
```

#### `bash` - Interactive Shell
```bash
docker run -it --rm -v "$(pwd):/data" \
  aljoshakoecher/caskade-planner:latest bash
```

### Legacy Commands (Still Supported)

For backward compatibility, the original commands still work:

```bash
# Original CLI usage
docker run -it --rm -v "$(pwd):/data" \
  aljoshakoecher/caskade-planner:latest \
  caskade-planner-cli plan-from-file /data/my-ontology.ttl http://example.org/capabilities#RequiredCapability1
```

### Docker Compose Integration

For integration into larger systems, you can use Docker Compose:

```yaml
version: '3.8'
services:
  caskade-planner:
    image: aljoshakoecher/caskade-planner:latest
    ports:
      - "5000:5000"
    volumes:
      - ./data:/data
    # Default command starts REST API
    # Override with: command: ["plan-from-file", "/data/ontology.ttl", "http://cap.iri"]
```

### Notes

- **File Access**: Mount your local directory with `-v "$(pwd):/data"` to access local ontology files from within the container
- **Network Access**: Use `host.docker.internal` instead of `localhost` to access services on your host machine from within the container
- **Data Persistence**: Results can be saved to mounted volumes using the file output options
- **Health Checks**: The REST API includes a health check endpoint at `/ping` for monitoring

### Python Integration

If you want to integrate CaSkade-Planner directly into your Python scripts, you can use it as a library.

#### Installation

Using pip:
```bash
pip install caskade-planner
```

Using Poetry:
```bash
poetry add caskade-planner
```

#### Basic Usage

```python
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.planning_result import PlanningResultType

# Create planner instance with required capability
planner = CaskadePlanner("http://example.org/capabilities#RequiredCapability1")

# Option 1: Load ontology from file
planner.with_file_query_handler("my-ontology.ttl")

# Option 2: Use SPARQL endpoint
# planner.with_endpoint_query_handler("localhost:7200/repositories/test-repo")

# Run planning
result = planner.cask_to_smt(max_happenings=20)

# Process results
if result.result_type == PlanningResultType.SAT:
    print(f"Plan found with {result.plan.plan_length} steps")
    for step in result.plan.plan_steps:
        print(f"Step {step.step_number}:")
        for cap in step.capability_appearances:
            print(f"  - {cap.capability_iri}")
else:
    print("No plan found")
```

#### Advanced Usage

```python
# Save intermediate files for debugging
result = planner.cask_to_smt(
    max_happenings=20,
    problem_location="problem.smt",  # Save SMT problem
    model_location="model.json",     # Save Z3 model
    plan_location="plan.json"        # Save structured plan
)

# Convert result to JSON
import json
result_json = result.to_json()
print(json.dumps(result_json, indent=2))
```