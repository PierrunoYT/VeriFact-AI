from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from fact_checker import fact_check, analyze_image_and_fact
from elasticsearch_operations import index_fact_check, search_fact_checks
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
                index_fact_check(statement, result, image_path)
                os.remove(image_path)  # Clean up the uploaded file
            else:
                result_generator = fact_check(statement, language)
                for chunk in result_generator:
                    result += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                index_fact_check(statement, result)
        
        return Response(stream_with_context(generate()), content_type='text/event-stream')
    
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    results = search_fact_checks(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
