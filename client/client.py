#172.16.46.72
from flask import Flask, request, render_template_string
import requests
from getmac import get_mac_address

app = Flask(__name__)

# Detect the MAC address of the current PC
mac_address = get_mac_address()

ALLOWED_EXTENSIONS = {'py', 'c', 'cpp', 'cl', 'cu'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Send File</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            body {
                font-family: 'Times New Roman', sans-serif;
                background-color: #0D315B;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: #333;
            }
            .container {
                background: #fff;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 500px;
                text-align: center;
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
                color: #2c3e50;
            }
            form {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            input[type="file"] {
                display: block;
                margin-bottom: 20px;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 1em;
                width: 100%;
            }
            select {
                display: block;
                margin-bottom: 20px;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 1em;
                width: 100%;
                background-color: #ecf0f1;
            }
            .hidden {
                display: none;
            }
            input[type="text"], input[type="password"] {
                display: block;
                margin-bottom: 20px;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 1em;
                width: 100%;
            }
            button {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 1.2em;
                margin-top: 20px;
                width: 100%;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            button:hover {
                background-color: #1c638d;
                transform: translateY(-2px);
            }
            .modal {
                display: none; 
                position: fixed;
                z-index: 1; 
                left: 0;
                top: 0;
                width: 100%; 
                height: 100%; 
                overflow: auto; 
                background-color: rgba(0, 0, 0, 0.4);
            }
            .modal-content {
                background-color: white;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 80%;
                max-width: 400px;
                text-align: center;
                border-radius: 10px;
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
            }
            .close:hover,
            .close:focus {
                color: black;
                text-decoration: none;
                cursor: pointer;
            }
            .modal-button {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 1em;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            .modal-button:hover {
                background-color: #1c638d;
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Send File</h1>
            <form id="uploadForm" method="post" enctype="multipart/form-data" action="/envoyer">
                <input type="file" name="file" required>
                <select name="device_choice" id="deviceChoice" required>
                    <option value="rpi1">Raspberry Pi 1</option>
                    <option value="rpi2">Raspberry Pi 2</option>
                    <option value="odroid">Odroid</option>
                    <option value="other">Other Device</option>
                </select>
                <div id="otherDeviceFields" class="hidden">
                    <input type="text" name="other_ip" placeholder="IP Address">
                    <input type="text" name="other_username" placeholder="Username">
                    <input type="password" name="other_password" placeholder="Password">
                </div>
                <button type="submit">Envoyer</button>
            </form>
        </div>
        <div id="myModal" class="modal">
            <div class="modal-content">
                <span class="close">&times;</span>
                <p id="modalText"></p>
                <button class="modal-button" id="closeModal">OK</button>
            </div>
        </div>
        <script>
            var modal = document.getElementById("myModal");
            var modalText = document.getElementById("modalText");
            var closeModalButton = document.getElementById("closeModal");
            var span = document.getElementsByClassName("close")[0];

            var deviceChoice = document.getElementById('deviceChoice');
            var otherDeviceFields = document.getElementById('otherDeviceFields');

            deviceChoice.addEventListener('change', function() {
                if (deviceChoice.value === 'other') {
                    otherDeviceFields.classList.remove('hidden');
                } else {
                    otherDeviceFields.classList.add('hidden');
                }
            });

            document.getElementById('uploadForm').onsubmit = function(event) {
                event.preventDefault();
                var formData = new FormData(this);
                fetch('/envoyer', {
                    method: 'POST',
                    body: formData
                }).then(response => response.text())
                .then(text => {
                    if (text.includes('Invalid file type')) {
                        modalText.textContent = 'Invalid file type. Only .py, .c, .cpp, .cl, .cu files are allowed.';
                    } else if (text.includes('No file part') || text.includes('No selected file')) {
                        modalText.textContent = 'No file part or no selected file.';
                    } else {
                        modalText.textContent = text;
                    }
                    modal.style.display = "block";
                }).catch(error => {
                    console.error('Error:', error);
                    modalText.textContent = 'An error occurred. Please try again.';
                    modal.style.display = "block";
                });
            };

            closeModalButton.onclick = function() {
                modal.style.display = "none";
            }

            span.onclick = function() {
                modal.style.display = "none";
            }

            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/envoyer', methods=['POST'])
def envoyer_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        files = {'file': (file.filename, file.stream, file.content_type)}
        device_choice = request.form.get('device_choice')

        if device_choice == 'other':
            other_ip = request.form.get('other_ip')
            other_username = request.form.get('other_username')
            other_password = request.form.get('other_password')
            response = requests.post(
                f'http://192.168.1.113:5000/envoyer?device={device_choice}&mac={mac_address}&other_ip={other_ip}&other_username={other_username}&other_password={other_password}',
                files=files
            )
        else:
            response = requests.post(
                f'http://192.168.1.113:5000/envoyer?device={device_choice}&mac={mac_address}',
                files=files
            )
        
        # Print device choice, MAC address, and response text to console
        print(f"File successfully sent to {device_choice} ({response.text}) with MAC address {mac_address}")

        return response.text
    else:
        return 'Invalid file type', 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
