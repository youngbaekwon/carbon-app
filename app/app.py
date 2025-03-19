# app/app.py

import os
# from flask import Flask
from flask import Flask, request
import psycopg2
import requests

app = Flask(__name__)

def call_internal_service(internal_service_host):
    """내부 서비스를 호출하고 응답을 반환하는 함수"""
    internal_service_host = os.environ.get('INTERNAL_SERVICE_HOST', 'hello-gke-service-internal') # 환경 변수 또는 기본값
    try:
        response = requests.get(f"http://{internal_service_host}:80/internal") # 내부 서비스 URL 변경 (http:// 추가)
        response.raise_for_status()  # 응답 상태 코드가 200 OK가 아니면 예외 발생
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error calling internal service: {str(e)}"
    
@app.route('/')
def hello():
    internal_host = request.args.get('internal_host') # 쿼리 파라메터에서 internal_host 값 가져오기
    print(f"internal_service_host: {internal_host}")
    if not internal_host:
        internal_service_message = "Internal Service Host 파라메터가 필요합니다." # 파라메터 없을 경우 에러 메시지
    # else:
        # internal_service_message = call_internal_service(internal_host)

    # Cloud SQL Proxy는 localhost:5432에서 리스닝
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],  # 127.0.0.1
        database=os.environ['DB_NAME'],  # testdb
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=5432
    )
    try:
        cur = conn.cursor()
        cur.execute("SELECT test_column FROM testtable;")
        results = cur.fetchall() # fetchall()로 변경하여 모든 행 가져오기
        db_values = [row[0] for row in results] # 리스트 컴프리헨션으로 값 추출
        db_result = ", ".join(db_values) # 쉼표로 구분된 문자열로 변환
        cur.close()
    except Exception as e:
        db_result = f"Database error: {str(e)}"
    finally:
        conn.close()

    # 내부 서비스 호출 및 메시지 저장
    internal_service_message = call_internal_service(internal_host)
    
    # 최종 응답 문자열 생성 (DB 결과와 내부 서비스 메시지 포함)
    response_message = f"DB Values: {db_result}<br>Internal Service Message: {internal_service_message}" # HTML br 태그 추가 (줄바꿈)
    return response_message

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)