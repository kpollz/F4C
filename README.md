# Giải pháp Dự đoán Nhu cầu Canteen

## Tổng quan

Đây là giải pháp toàn diện để dự đoán nhu cầu ăn trưa trong canteen công ty, giúp tối ưu hóa việc chuẩn bị thức ăn và giảm thiểu lãng phí.

## Vấn đề

- Công ty có 2000+ nhân viên chia theo nhiều tầng
- Mỗi tầng có giờ ăn khác nhau
- Canteen có nhiều line đồ ăn (counter)
- **Vấn đề**: Line đồ ăn ngon hết trước khi các tầng ăn sau đến
- **Nguyên nhân**: Không dự đoán được dung lượng suất ăn của từng line

## Giải pháp

### 1. Phân tích dữ liệu (`canteen_analysis.py`)

- **Trực quan hóa dữ liệu**: Biểu đồ phân tích xu hướng, phân bố theo counter, department
- **Phân tích pattern**: Tìm hiểu thói quen ăn uống của nhân viên
- **Dashboard tương tác**: Giao diện Plotly để khám phá dữ liệu

### 2. Dự đoán nhu cầu (`demand_forecasting.py`)

- **Machine Learning**: Random Forest, XGBoost
- **Feature Engineering**: 
  - Thời gian (giờ, ngày trong tuần, tháng)
  - Lịch sử nhu cầu
  - Thông tin menu (kcal, loại món, độ phổ biến)
  - Phòng ban và sở thích
- **Ensemble Methods**: Kết hợp nhiều model để tăng độ chính xác

## Cài đặt

```bash
pip install -r requirements.txt
```

## Sử dụng

### 1. Phân tích dữ liệu

```python
from canteen_analysis import CanteenAnalyzer

analyzer = CanteenAnalyzer()

# Load dữ liệu
analyzer.load_menu_data("menu_data.json")
analyzer.load_transaction_data("transaction_data.xlsx")

# Phân tích pattern
patterns = analyzer.analyze_transaction_patterns()

# Tạo biểu đồ
analyzer.visualize_data()
analyzer.create_interactive_dashboard()
```

### 2. Dự đoán nhu cầu

```python
from demand_forecasting import CanteenDemandForecaster

forecaster = CanteenDemandForecaster()

# Xử lý dữ liệu
processed_data = forecaster.preprocess_data(transaction_data, menu_data)
feature_data = forecaster.engineer_features(processed_data)

# Huấn luyện model
X, y = forecaster.prepare_features(feature_data)
models = forecaster.train_models(X, y)

# Dự đoán
predictions = forecaster.predict_demand(menu_data, "2024-02-01", 12)
```

## Cấu trúc dữ liệu

### Menu Data (JSON)
```json
{
  "date": "2024-01-15",
  "menus": [
    {
      "corner": "01",
      "corner_index": 1,
      "main": "Cơm gà xối mỡ",
      "dishes": ["Canh chua cá lóc", "Rau muống xào tỏi"],
      "kcal": 650
    }
  ]
}
```

### Transaction Data (Excel)
| Meal Date | Food Distribution Counter | Company | Employee No | Name | Dept. |
|-----------|--------------------------|---------|-------------|------|-------|
| 2024-01-15 11:30 | 01 | Company A | EMP001 | John Doe | IT |

## Tính năng chính

### 1. Phân tích Pattern
- **Xu hướng theo thời gian**: Phân tích nhu cầu theo giờ, ngày, tháng
- **Phân bố theo counter**: Tìm hiểu sở thích của nhân viên
- **Phân tích theo phòng ban**: Hiểu thói quen ăn uống của từng bộ phận

### 2. Feature Engineering
- **Time-based features**: Giờ, ngày trong tuần, tháng, mùa
- **Historical features**: Nhu cầu trung bình, độ lệch chuẩn
- **Menu features**: Loại món, kcal, độ phổ biến
- **Department features**: Sở thích theo phòng ban

### 3. Modeling
- **Random Forest**: Xử lý tốt dữ liệu không tuyến tính
- **XGBoost**: Tối ưu hóa hiệu suất
- **Ensemble**: Kết hợp để tăng độ chính xác

### 4. Evaluation Metrics
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error
- **R²**: Coefficient of determination

## Quy trình triển khai

### Phase 1: Thu thập và chuẩn bị dữ liệu
1. Thu thập lịch sử quẹt thẻ ăn
2. Thu thập menu hàng ngày
3. Làm sạch và validate dữ liệu

### Phase 2: Phân tích và khám phá
1. Trực quan hóa dữ liệu
2. Phân tích pattern
3. Xác định features quan trọng

### Phase 3: Xây dựng model
1. Feature engineering
2. Huấn luyện model
3. Đánh giá hiệu suất

### Phase 4: Triển khai
1. Tích hợp vào hệ thống
2. Monitoring và retraining
3. Cập nhật liên tục

## Lợi ích

### 1. Giảm lãng phí
- Dự đoán chính xác nhu cầu
- Chuẩn bị đúng lượng thức ăn
- Giảm chi phí nguyên liệu

### 2. Tăng trải nghiệm nhân viên
- Đảm bảo có đủ thức ăn ngon
- Giảm thời gian chờ đợi
- Tăng sự hài lòng

### 3. Tối ưu hóa vận hành
- Lập kế hoạch hiệu quả
- Giảm chi phí vận hành
- Tăng hiệu suất canteen

## Hướng phát triển

### 1. Mở rộng features
- Thêm dữ liệu thời tiết
- Phân tích sentiment của menu
- Tích hợp dữ liệu sức khỏe

### 2. Cải thiện model
- Deep Learning (LSTM, GRU)
- Time series forecasting
- Real-time prediction

### 3. Tích hợp hệ thống
- API endpoints
- Real-time dashboard
- Automated alerts

## Tác giả

Giải pháp được phát triển để giải quyết bài toán thực tế về quản lý canteen công ty.

## License

MIT License
