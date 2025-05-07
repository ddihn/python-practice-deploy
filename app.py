# -*- coding: utf-8 -*-
# (배포용) 모델서빙_거래량 총합계 반환 서비스

# 서버 관리용 fast api 의존 라이브러리
import uvicorn
from fastapi import FastAPI
import pickle
import numpy as np
import pandas as pd
from pydantic import BaseModel
from sqlalchemy import create_engine
import nest_asyncio
from pyngrok import ngrok
from fastapi.middleware.cors import CORSMiddleware

# CORS 설정
app = FastAPI(title="TOTAL_SUM API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# MySQL 데이터베이스 연결 정보 설정
user = ''
password = ''
host = ''
port = '3306'
database = ''
myngine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

# 입력 데이터 모델 정의
class InDataset(BaseModel):
    targetYear: str

# 총합 예측 API
@app.post("/predictSumQty", status_code=200)
async def predict_tf(x: InDataset):
    inTargetYear = x.targetYear
    response = totalQtySum(inTargetYear)
    return {"prediction": response}

@app.get("/")
async def root():
    return {"message": "online"}

# 예측 함수 정의
def totalQtySum(inYear):
    query = """
        SELECT SUM(QTY) AS sum_qty
        FROM feature_regression_example
        WHERE year = %s
    """
    resultDf = pd.read_sql(sql=query, con=myngine, params=[inYear])
    result = resultDf["sum_qty"].values[0]
    return result

# 서버 시작
if __name__ == "__main__":
    auth_token = ""
    ngrok.set_auth_token(auth_token)
    ngrokTunnel = ngrok.connect(9999)
    print("공용 URL:", ngrokTunnel.public_url)

    nest_asyncio.apply()
    uvicorn.run(app, host="0.0.0.0", port=9999)
