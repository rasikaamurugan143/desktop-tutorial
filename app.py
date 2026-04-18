from flask import Flask, request, jsonify, render_template

from srd.predict import predict_url

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        # Use the predict_url function from the existing project
        result = predict_url(url)
        
        # Parse the result string to determine type and confidence
        is_phishing = "🚨" in result or "Phishing" in result
        
        return jsonify({
            'success': True,
            'result': result,
            'is_phishing': is_phishing
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Run from the root folder so that it finds 'model/final_model.pkl' correctly
    print("Starting Premium Phishing Detector UI...")
    app.run(debug=True, port=8000)
