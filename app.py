from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from fact_checker import fact_check, analyze_image_and_fact
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage for user preferences
user_preferences = {
    'language': 'english',
    'method': 'combined'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        statement = request.form.get('statement', '')
        image = request.files.get('image')
        language = request.form.get('language', user_preferences['language'])
        method = request.form.get('method', user_preferences['method'])
        
        def generate():
            try:
                result = ""
                if image:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    result_generator = analyze_image_and_fact(statement, image_path, language, method)
                    for chunk in result_generator:
                        result += chunk
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                    os.remove(image_path)  # Clean up the uploaded file
                else:
                    result_generator = fact_check(statement, language, method)
                    for chunk in result_generator:
                        result += chunk
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
            except Exception as e:
                app.logger.error(f"Error during fact checking: {str(e)}")
                yield f"data: {json.dumps({'content': 'An error occurred during processing. Please try again.'})}\n\n"
        
        return Response(stream_with_context(generate()), content_type='text/event-stream')
    
    return render_template('index.html')

@app.route('/user-preferences', methods=['GET', 'POST'])
def user_preferences_route():
    global user_preferences
    if request.method == 'POST':
        data = request.json
        user_preferences['language'] = data.get('language', user_preferences['language'])
        user_preferences['method'] = data.get('method', user_preferences['method'])
        return jsonify({"message": "Preferences updated successfully"}), 200
    else:
        return jsonify(user_preferences), 200

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
