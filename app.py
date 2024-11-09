from flask import Flask

# 다른 모듈에서 블루프린트 가져오기
from predictrouter import predict_bp

app = Flask(__name__)


# 블루프린트 등록
app.register_blueprint(predict_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    