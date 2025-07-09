# Chi tiết Giải pháp Dự đoán Nhu cầu Canteen

## 1. Cách trực quan hóa dữ liệu

### A. Phân tích cơ bản (`canteen_analysis.py`)

Tôi đã tạo 6 loại biểu đồ chính để phân tích dữ liệu:

#### 1. Daily Transaction Trend (Xu hướng giao dịch theo ngày)
```python
# Biểu đồ đường thể hiện số lượng giao dịch theo thời gian
axes[0, 0].plot(daily_counts.index, daily_counts.values, marker='o')
```
- **Mục đích**: Phát hiện xu hướng, mùa vụ, ngày đặc biệt
- **Insight**: Thứ 2-6 cao hơn cuối tuần, có thể có ngày nghỉ lễ
- **Ứng dụng**: Lập kế hoạch nhân sự, chuẩn bị nguyên liệu

#### 2. Counter Distribution (Phân bố theo counter)
```python
# Biểu đồ tròn thể hiện tỷ lệ sử dụng từng counter
axes[0, 1].pie(counter_dist.values, labels=counter_dist.index, autopct='%1.1f%%')
```
- **Mục đích**: Xem counter nào được ưa chuộng nhất
- **Insight**: Counter 01 (cơm gà) có thể được ưa chuộng hơn
- **Ứng dụng**: Tối ưu hóa menu, phân bổ nhân sự

#### 3. Department Distribution (Phân bố theo phòng ban)
```python
# Biểu đồ cột thể hiện số lượng giao dịch theo phòng ban
axes[0, 2].bar(dept_dist.index, dept_dist.values)
```
- **Mục đích**: Hiểu thói quen ăn uống của từng bộ phận
- **Insight**: IT, HR có thể ăn sớm hơn, Sales ăn muộn hơn
- **Ứng dụng**: Lập lịch ăn theo phòng ban

#### 4. Hourly Distribution (Phân bố theo giờ)
```python
# Biểu đồ cột thể hiện số lượng giao dịch theo giờ
axes[1, 0].bar(time_dist.index, time_dist.values)
```
- **Mục đích**: Tìm giờ cao điểm
- **Insight**: 11:30-12:30 là giờ cao điểm
- **Ứng dụng**: Lập kế hoạch nhân sự theo giờ

#### 5. Counter vs Department Heatmap (Bản đồ nhiệt)
```python
# Heatmap thể hiện mối quan hệ giữa counter và phòng ban
sns.heatmap(counter_dept, annot=True, fmt='d', cmap='YlOrRd')
```
- **Mục đích**: Tìm sở thích của từng phòng ban với từng counter
- **Insight**: IT thích counter 01, Sales thích counter 03
- **Ứng dụng**: Tùy chỉnh menu theo phòng ban

#### 6. Time Series by Counter (Xu hướng thời gian theo counter)
```python
# Biểu đồ đường thể hiện xu hướng theo giờ của từng counter
time_counter.plot(kind='line', marker='o')
```
- **Mục đích**: So sánh xu hướng của các counter theo thời gian
- **Insight**: Counter nào có xu hướng tăng/giảm
- **Ứng dụng**: Dự đoán nhu cầu theo thời gian

### B. Dashboard tương tác (Plotly)

Tôi cũng tạo dashboard tương tác với Plotly để:
- **Zoom in/out**: Phóng to thu nhỏ biểu đồ
- **Hover information**: Thông tin chi tiết khi di chuột
- **Filter**: Lọc theo thời gian, counter, phòng ban
- **Export**: Xuất biểu đồ

## 2. Giải pháp dự đoán nhu cầu

### A. Kiến trúc tổng thể

```
Input Data → Preprocessing → Feature Engineering → Model Training → Prediction
```

### B. Feature Engineering (Tạo đặc trưng)

#### 1. Time-based Features:
```python
# Thời gian
'Hour': 11, 12, 13
'DayOfWeek': 0-6 (Thứ 2-Chủ nhật)
'Month': 1-12
'WeekOfYear': 1-52
'IsWeekend': 0/1
```

**Mục đích**: 
- Phát hiện pattern theo thời gian
- Xử lý mùa vụ, ngày đặc biệt
- Dự đoán nhu cầu theo giờ

#### 2. Historical Features:
```python
# Lịch sử nhu cầu
'HistMean': Nhu cầu trung bình theo counter, giờ, ngày
'HistStd': Độ lệch chuẩn
```

**Mục đích**:
- Sử dụng dữ liệu lịch sử để dự đoán
- Đánh giá độ ổn định của nhu cầu
- Xử lý outliers

#### 3. Menu Features:
```python
# Đặc trưng menu
'CornerIndex': 1, 2, 3, 4
'SideDishes': Số món phụ
'Kcal': Calorie
'DishType': rice, noodle_soup, grilled, other
'IsPopular': 0/1 (dựa trên từ khóa)
```

**Mục đích**:
- Phân tích sở thích theo loại món
- Dự đoán dựa trên độ phổ biến
- Tối ưu hóa menu

#### 4. Department Features:
```python
# Đặc trưng phòng ban
'DeptPreference': Sở thích của phòng ban với counter
```

**Mục đích**:
- Hiểu sở thích của từng phòng ban
- Dự đoán theo pattern của phòng ban
- Tùy chỉnh menu theo bộ phận

### C. Modeling Strategy

#### 1. Multiple Models:
```python
# Random Forest
rf_model = RandomForestRegressor(n_estimators=100)
# XGBoost  
xgb_model = xgb.XGBRegressor(n_estimators=100)
```

**Lý do chọn**:
- **Random Forest**: Xử lý tốt dữ liệu không tuyến tính, ít overfitting
- **XGBoost**: Hiệu suất cao, xử lý tốt dữ liệu lớn

#### 2. Ensemble Method:
```python
# Kết hợp dự đoán của nhiều model
ensemble_pred = np.mean([rf_pred, xgb_pred], axis=0)
```

**Lợi ích**:
- Giảm variance của dự đoán
- Tăng độ chính xác
- Ổn định hơn

#### 3. Evaluation Metrics:
- **MAE**: Mean Absolute Error (lỗi tuyệt đối trung bình)
- **RMSE**: Root Mean Square Error (lỗi bình phương trung bình)
- **R²**: Coefficient of determination (hệ số xác định)

### D. Prediction Process

#### 1. Input:
```python
# Menu của ngày mai
menu_data = {
    "date": "2024-02-01",
    "menus": [
        {
            "corner": "01",
            "corner_index": 1,
            "main": "Cơm gà xối mỡ",
            "dishes": ["Canh chua cá lóc", "Rau muống xào tỏi"],
            "kcal": 650
        },
        # ... other menus
    ]
}

# Thời gian dự đoán
hour = 12
```

#### 2. Feature Creation:
```python
# Tạo features cho từng counter
for menu in day_menu['menus']:
    features = {
        'Hour': 12,
        'DayOfWeek': 3,  # Thứ 5
        'CornerIndex': menu['corner_index'],
        'Kcal': menu['kcal'],
        'DishType': self._categorize_dish(menu['main']),
        'IsPopular': self._is_popular_dish(menu['main']),
        # ... other features
    }
```

#### 3. Prediction:
```python
# Dự đoán cho từng counter
predictions = [
    {'Corner': '01', 'PredictedDemand': 45},
    {'Corner': '02', 'PredictedDemand': 38},
    {'Corner': '03', 'PredictedDemand': 42},
    {'Corner': '04', 'PredictedDemand': 35}
]
```

## 3. Lợi ích của giải pháp

### A. Ngay lập tức:
- **Giảm lãng phí**: Dự đoán chính xác hơn → chuẩn bị đúng lượng
- **Tăng trải nghiệm**: Đảm bảo có đủ thức ăn ngon
- **Tiết kiệm chi phí**: Giảm chi phí nguyên liệu

### B. Dài hạn:
- **Real-time prediction**: Dự đoán theo thời gian thực
- **Mobile app**: Nhân viên có thể xem menu và đặt trước
- **Automated inventory**: Tự động quản lý kho nguyên liệu

## 4. Quy trình triển khai

### Phase 1 (Tuần 1-2):
- Thu thập dữ liệu lịch sử quẹt thẻ
- Thu thập menu hàng ngày
- Triển khai hệ thống cơ bản
- **Kết quả mong đợi**: Có thể dự đoán với độ chính xác 70-80%

### Phase 2 (Tháng 1-2):
- Tối ưu hóa model dựa trên dữ liệu thực
- Thêm features mới (thời tiết, sự kiện)
- Tích hợp với hệ thống quản lý canteen
- **Kết quả mong đợi**: Độ chính xác tăng lên 85-90%

### Phase 3 (Tháng 3-6):
- Real-time prediction system
- Mobile app cho nhân viên
- Automated inventory management
- **Kết quả mong đợi**: Hệ thống hoàn chỉnh, tự động

## 5. Metrics và KPI

### A. Technical Metrics:
- **MAE**: < 5 suất ăn
- **RMSE**: < 7 suất ăn
- **R²**: > 0.8

### B. Business Metrics:
- **Giảm lãng phí**: 20-30%
- **Tăng sự hài lòng**: 15-25%
- **Tiết kiệm chi phí**: 10-15%

## 6. Rủi ro và Giải pháp

### A. Rủi ro:
- **Dữ liệu không đầy đủ**: Thiếu lịch sử quẹt thẻ
- **Thay đổi pattern**: Nhân viên thay đổi thói quen
- **Sự kiện đặc biệt**: Ngày lễ, sự kiện công ty

### B. Giải pháp:
- **Data validation**: Kiểm tra chất lượng dữ liệu
- **Model retraining**: Cập nhật model định kỳ
- **Manual override**: Cho phép điều chỉnh thủ công

## 7. Hướng phát triển

### A. Short-term (3-6 tháng):
- Thêm dữ liệu thời tiết
- Phân tích sentiment của menu
- Tích hợp với hệ thống HR

### B. Long-term (6-12 tháng):
- Deep Learning (LSTM, GRU)
- Real-time prediction
- AI-powered menu optimization

## 8. Kết luận

Giải pháp này cung cấp:
- **Phân tích toàn diện**: Hiểu rõ pattern và xu hướng
- **Dự đoán chính xác**: Giảm lãng phí và tăng hiệu quả
- **Khả năng mở rộng**: Có thể áp dụng cho nhiều canteen
- **ROI tích cực**: Tiết kiệm chi phí và tăng trải nghiệm

Với việc triển khai đúng cách, giải pháp này sẽ mang lại lợi ích đáng kể cho công ty trong việc quản lý canteen hiệu quả. 