### **사용자 메뉴얼: Star Info Web API**

---

### **1. 개요**

Star Info Web API는 천문학 데이터를 기반으로 다양한 정보를 제공하는 RESTful API입니다. 사용자는 다음 데이터를 조회할 수 있습니다:

- 혜성 접근 이벤트 정보
- 별자리 가시성
- 유성우 활동 및 가시성
- 특정 날짜의 달의 위상
- 행성의 가시성 및 대접근 이벤트
- 특정 위치와 날짜의 일출 및 일몰 시간

---

### **2. 주요 기능**

### **2.1. 혜성 정보 (Comets)**

- **Endpoint**: `/api/comet/approach`
- **Method**: `GET`
- **기능**: 특정 혜성의 접근 이벤트를 조회합니다.
- **사용 예시**:
    
    ```bash

    curl -X GET "http://<server-ip>:5555/api/comet/approach?comet=Halley&start_date=2024-10-01&range_days=365"
    
    ```
    

---

### **2.2. 별자리 정보 (Constellations)**

- **Endpoint**: `/api/constellations/visibility`
- **Method**: `GET`
- **기능**: 사용자의 위치와 시간대에 따라 관측 가능한 별자리 정보를 조회합니다.
- **사용 예시**:
    
    ```bash

    curl -X GET "http://<server-ip>:5555/api/constellations/visibility?lat=37.5665&lon=126.9780&start_date=2024-10-01&end_date=2024-10-07"
    
    ```
    

---

### **2.3. 유성우 정보 (Meteor Showers)**

- **Endpoint**:
    - `/api/meteor_shower/info` (GET)
    - `/api/meteor_shower/update` (POST)
    - `/api/meteor_shower/visibility` (GET)
- **기능**:
    - `info`: 혜성을 기반으로 유성우 활동 정보를 반환.
    - `update`: 유성우 데이터를 업데이트.
    - `visibility`: 특정 유성우의 가시성을 평가.
- **사용 예시**:
    
    ```bash

    # 유성우 정보 조회
    curl -X GET "http://<server-ip>:5555/api/meteor_shower/info?comet=Halley&start_date=2024-10-01&range_days=365"
    
    # 유성우 데이터 업데이트
    curl -X POST "http://<server-ip>:5555/api/meteor_shower/update"
    
    # 유성우 가시성 평가
    curl -X GET "http://<server-ip>:5555/api/meteor_shower/visibility?name=Perseid&year=2024&latitude=37.5665&longitude=126.9780"
    
    ```
    

---

### **2.4. 달의 위상 정보 (Moon Phase)**

- **Endpoint**: `/api/moon/phase`
- **Method**: `GET`
- **기능**: 특정 날짜의 달의 위상을 반환합니다.
- **사용 예시**:
    
    ```bash

    curl -X GET "http://<server-ip>:5555/api/moon/phase?date=2024-10-01"
    
    ```
    

---

### **2.5. 행성 정보 (Planets)**

- **Endpoint**:
    - `/api/planets/visibility` (GET)
    - `/api/planets/opposition` (GET)
    - `/api/planets/update_raw_data` (POST)
- **기능**:
    - `visibility`: 특정 행성의 가시성을 반환.
    - `opposition`: 특정 행성의 대접근 이벤트를 반환.
    - `update_raw_data`: 대접근 이벤트 데이터를 업데이트.
- **사용 예시**:
    
    ```bash

    # 행성 가시성 조회
    curl -X GET "http://<server-ip>:5555/api/planets/visibility?planet=Mars&lat=37.5665&lon=126.9780&date=2024-10-01&range_days=7"
    
    # 행성 대접근 이벤트 조회
    curl -X GET "http://<server-ip>:5555/api/planets/opposition?planet=Jupiter&year=2024"
    
    # 행성 대접근 데이터 업데이트
    curl -X POST "http://<server-ip>:5555/api/planets/update_raw_data"
    
    ```
    

---

### **2.6. 일출 및 일몰 정보 (Sunrise & Sunset)**

- **Endpoint**: `/api/sunrise_sunset/time`
- **Method**: `GET`
- **기능**: 특정 위치와 날짜의 일출 및 일몰 시간을 반환합니다.
- **사용 예시**:
    
    ```bash
    curl -X GET "http://<server-ip>:5555/api/sunrise_sunset/time?lat=37.5665&lon=126.9780&start_date=2024-10-01&end_date=2024-10-07"
    ```
    

---

### **3. API 응답 구조**

### **성공 시 응답**:

- **HTTP 상태 코드**: `200 OK`
- **형식**: JSON
- **예시**:
    
    ```json
    {
        "location": {
            "latitude": 37.5665,
            "longitude": 126.9780
        },
        "data": [
            {
                "date": "2024-10-01",
                "sunrise": "06:18",
                "sunset": "18:10"
            }
        ]
    }
    
    ```
    

### **오류 발생 시 응답**:

- **HTTP 상태 코드**: `400 Bad Request` 또는 `500 Internal Server Error`
- **형식**: JSON
- **예시**:
    
    ```json
    {
        "error": "Invalid input format. Use YYYY-MM-DD."
    }
    
    ```
    

---

### **4. API 사용 시 주의 사항**

1. 모든 필수 매개변수를 정확히 전달해야 합니다.
2. 날짜 형식은 반드시 `YYYY-MM-DD`를 사용해야 합니다.
3. 좌표(위도/경도)는 소수점을 포함한 실수(float) 값으로 전달해야 합니다.

---

### **5. 참고 사항**

- API 사용 시 최대 요청 범위를 초과하지 않도록 주의하세요.
- Redis를 통한 캐싱을 활용해 빈번한 데이터 요청을 최적화합니다.
- 자세한 요청 형식 및 파라미터는 Swagger UI (`/api/docs`)를 통해 확인 가능합니다.
