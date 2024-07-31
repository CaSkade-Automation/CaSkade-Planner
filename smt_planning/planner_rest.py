import os
import tempfile
from flask import Flask, Response, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from flask_cors import CORS

from smt_planning.smt.cask_to_smt import CaskadePlanner

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt', 'ttl', 'xml', 'owl', 'json'}

# Create API 
app = Flask(__name__)
cors = CORS(app)
app.secret_key = 'the random string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename: str) -> bool:
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def setup_planner_with_file(files: ImmutableMultiDict[str, FileStorage], required_capability_iri: str) -> CaskadePlanner | tuple[Response, int]:
	if 'ontology-file' not in files:
		return jsonify({'error': 'No file part'}), 400
	
	file = files['ontology-file']
	# If the user does not select a file, the browser submits an
	# empty file without a filename.
	if file.filename == '' or not file.filename:
		return jsonify({'error': 'No selected file'}), 400
	
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(filename)

		planner = CaskadePlanner(required_capability_iri)
		planner.with_file_query_handler(filename)
		return planner
	else: 
		return jsonify({'error': 'File type not allowed'}), 400


@app.get('/ping')
def ping():
	return Response(status=204)

# Wait for POST requests with a query param ?mode to /plan
@app.post('/plan') # type: ignore
def generate_and_solve_plan():
	if (not request.is_json):
		return jsonify({"message": "Request must be JSON"}), 400
	
	# Get JSON request body
	data = request.get_json()
	mode = data.get('mode')
	required_capability_iri = data.get('requiredCapabilityIri')

	if mode == 'file':
		planner = setup_planner_with_file(request.files, required_capability_iri) # type: ignore
		# If the planner is a tuple, it contains an error response
		if isinstance(planner, tuple):
			return planner
		
	elif mode == 'sparql-endpoint':
		endpoint_url = data.get('endpointUrl')
		
		if not endpoint_url:
			return jsonify({'error': 'No endpoint-url provided'}), 400
		planner = CaskadePlanner(required_capability_iri)
		planner.with_endpoint_query_handler(endpoint_url)

	max_happenings = request.args.get('max-happenings',type=int)
	
	# In case None gets passed as a max_happening, set back to default value of 5
	if max_happenings == None:
		max_happenings = 5
	result = planner.cask_to_smt(max_happenings)
	if result.plan is None:
		# No plan found. The result contains the unsat core that explains why
		return jsonify(result.as_dict()), 404
	return result.as_dict()

def run():
	app.run()

if __name__ == '__main__': 
	run()