from flask import Flask, render_template

app = Flask(__name__)

@app.route('/emergency_progress', methods=['GET', 'POST'])
def emergency():
    return render_template('emergency_progress.html')

@app.route('/neighborhood_reviews', methods=['GET', 'POST'])
def neighborhood():
    return render_template('neighborhood_reviews.html')

@app.route('/digital_document', methods=['GET', 'POST'])
def digital_document():
    return render_template('digital_document.html')

@app.route('/driver_collaboration', methods=['GET', 'POST'])
def driver_collaboration():
    return render_template('driver_collaboration.html')

if __name__ == '__main__':
    app.run(debug=True) 


