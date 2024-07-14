from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from fact_checker import fact_check, analyze_image_and_fact
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime, timedelta
from algoliasearch.search_client import SearchClient

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Algolia client
client = SearchClient.create('YOUR_ALGOLIA_APP_ID', 'YOUR_ALGOLIA_API_KEY')
index = client.init_index('fact_checks')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        statement = request.form.get('statement', '')
        image = request.files.get('image')
        language = request.form.get('language', 'english')
        
        def generate():
            result = ""
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                result_generator = analyze_image_and_fact(statement, image_path, language)
                for chunk in result_generator:
                    result += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                os.remove(image_path)  # Clean up the uploaded file
            else:
                result_generator = fact_check(statement, language)
                for chunk in result_generator:
                    result += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        return Response(stream_with_context(generate()), content_type='text/event-stream')
    
    return render_template('index.html')

@app.route('/timeline', methods=['GET'])
def timeline():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        # Query Algolia to retrieve the relevant fact-checking data
        filters = []
        if start_date:
            filters.append(f"timestamp >= {start_date}")
        if end_date:
            filters.append(f"timestamp <= {end_date}")

        filter_string = " AND ".join(filters)
        
        search_results = index.search("", {
            'filters': filter_string,
            'attributesToRetrieve': ['statement', 'result', 'analysis', 'timestamp'],
            'hitsPerPage': 1000,  # Adjust as needed
        })

        # Prepare the data for the timeline visualization
        timeline_data = []
        for hit in search_results['hits']:
            timeline_data.append({
                'id': hit.get('objectID'),
                'content': hit.get('statement'),
                'start': hit.get('timestamp'),
                'result': hit.get('result'),
                'analysis': hit.get('analysis')
            })

        return jsonify(timeline_data)
    except Exception as e:
        print(f"Error generating timeline view: {e}")
        return jsonify({'error': 'Failed to generate the timeline view.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
