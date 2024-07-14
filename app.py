from flask import Flask, render_template, request, jsonify
from fact_checker import fact_check, analyze_image_and_fact
import os
from werkzeug.utils import secure_filename

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
        
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            result = analyze_image_and_fact(statement, image_path)
            os.remove(image_path)  # Clean up the uploaded file
        else:
            result = fact_check(statement)
        
        return jsonify({'result': result})
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
