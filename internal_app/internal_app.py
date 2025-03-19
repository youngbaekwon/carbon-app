from flask import Flask

internal_app = Flask(__name__)

@internal_app.route('/internal')
def internal_hello():
    return "Hello from internal service!"

if __name__ == '__main__':
    internal_app.run(host='0.0.0.0', port=8081) # 내부 서비스는 8081 포트 사용