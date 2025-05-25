from routes import app

if __name__ == '__main__':
    PORT_NUMBER = 5001
    print("-"*70)
    print(f"Welcome to The Sydney Automotive Group.\nPlease open your browser to: http://127.0.0.1:{PORT_NUMBER}")
    print("-"*70)
    app.run(debug=True, host='0.0.0.0', port=PORT_NUMBER)
