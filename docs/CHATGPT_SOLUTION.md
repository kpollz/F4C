**1. Phân tích bài toán**

* **Bối cảnh & vấn đề**

  * Công ty có >2000 nhân sự, ăn trưa theo ca (tầng này, tầng kia có khung giờ khác nhau).
  * Canteen có nhiều “line” (cửa phát đồ ăn), mỗi line phục vụ menu khác nhau.
  * Khi ca sau, nhân viên thường không còn suất ở line “hot” vì demand cao, dẫn đến trải nghiệm không đồng đều.
  * Nguyên nhân gốc: bếp không biết trước số suất cần chuẩn bị cho từng line dựa trên menu cụ thể.

* **Mục tiêu**

  * Dự đoán **dung lượng (số suất)** cần chuẩn bị cho mỗi line trong ngày, dựa trên:

    1. **Lịch sử quẹt thẻ** (ai ăn ngày nào, line nào)
    2. **Menu ngày** (tên món chính, món phụ, kcal, corner\_index…)

* **Thách thức chính**

  1. **Seasonality & trend**: lượng người ăn thay đổi theo ngày trong tuần, thời tiết, ngày lễ…
  2. **Menu attractiveness**: một số món “hấp dẫn” luôn được chọn nhiều hơn, phụ thuộc vào tên món, kcal, kết hợp món phụ…
  3. **Ca & phân tầng**: giờ ăn khác nhau, nhân khẩu học giữa các tầng (vd: nhân viên văn phòng vs kỹ thuật) có thể ưa món khác nhau.
  4. **Thiếu tín hiệu phụ**: như thời tiết, khuyến mãi, feedback chất lượng…

**2. Các bài toán tương tự trong nghiên cứu**

* **Demand Forecasting cho căng‑tin/trường học**

  * “Demand Forecasting for Food Production Using Machine Learning Algorithms: A Case Study of University Refectory” – ACI & YERGÖK (2023) phát triển 18 mô hình (ANN, Random Forest, XGBoost…) dựa trên lịch sử tiêu thụ và thành phần món ăn ([pdfs.semanticscholar.org][1]).
* **ML cho dự báo nhu cầu trong căng‑tin học đường**

  * “Machine Learning Techniques for Cafeteria Demand Forecasting: An Institutional Case” – Aydın et al. (May 2025) sử dụng dữ liệu quẹt thẻ, thông tin menu để so sánh hiệu quả giữa Decision Tree, XGBoost, Prophet… ([dergipark.org.tr][2]).
* **Demand Sensing**

  * Phương pháp “Demand sensing” tích hợp tín hiệu thực tế (POS, quẹt thẻ, cảm biến) để điều chỉnh dự báo nhanh chóng theo diễn biến thực tế ([Wikipedia][3]).

**3. Trực quan hóa dữ liệu thô**

> *Lưu ý: do chưa có dữ liệu mẫu cụ thể, dưới đây là gợi ý các loại biểu đồ và cách dựng.*

1. **Biểu đồ phân phối số lượt quẹt theo line**

   * Bar chart: trục x là `corner_index` (line 1,2,3…), trục y là tổng lượt quẹt trong ngày/tuần.
2. **Time series lượt quẹt theo ca và ngày**

   * Line plot: mỗi ca (ví dụ 11h–11h30, 11h30–12h…), so sánh xu hướng theo ngày để nhận diện ngày cao điểm/thấp điểm.
3. **Heatmap ca × line**

   * Ma trận màu thể hiện mật độ quẹt (count) tại từng ô (ca\_i, line\_j), dễ thấy ca nào line nào “cháy”.
4. **Phân tích tương quan menu vs. lượt chọn**

   * Scatter plot hoặc boxplot: kcal của món chính (hoặc số lượng món phụ) vs. lượt chọn, giúp đánh giá món “nặng”/“nhẹ” ảnh hưởng thế nào.

**4. Đề xuất giải pháp**

1. **Xây dựng pipeline dữ liệu**

   * **ETL**:

     1. Đọc JSON menu hàng ngày, flatten thành bảng: `date, corner_index, main, dishes_count, kcal`.
     2. Đọc Excel log quẹt: `Meal Date, corner_index, Employee No, Dept.`
     3. Join theo ngày và line để tạo record `N` lượt chọn của line `i` ngày `t`.
   * **Feature engineering**:

     * Thêm biến ngày trong tuần, holiday flag, ca (morning/late), Dept. nhóm tầng.
     * Biến menu: embedding từ tên chính, số món phụ, kcal.
2. **Mô hình dự báo**

   * **Baseline**: ARIMA / Holt–Winters theo series mỗi line.
   * **Machine Learning**:

     * Tree‑based: Random Forest, XGBoost, LightGBM (dễ interpret và handle categorical).
     * Deep Learning: LSTM, DeepAR (cho probabilistic forecasting) ([arXiv][4]).
   * **Ensemble**: kết hợp dự báo theo line riêng lẻ và dự báo tổng, tối ưu portfolio.
3. **Đánh giá & triển khai**

   * **Metrics**: MAE, RMSE, MAPE trên tập validation (chia theo thời gian).
   * **Monitoring**: dashboard hiển thị forecast vs. actual hàng ngày, cảnh báo khi lệch > x%.
   * **Tính mở rộng**: có thể tính thêm yếu tố thời tiết, feedback chất lượng, campaign nội bộ.
4. **Tối ưu & mở rộng**

   * Cân nhắc **price elasticity** nếu áp dụng giá khác nhau.
   * Dùng **reinforcement learning** để đề xuất số suất tối ưu, cân bằng giữa over‑production và under‑production.
   * Triển khai mô‑đun tự động gợi ý rotation menu dựa trên lịch sử để cân bằng nhu cầu.

> Với quy trình này, bếp sẽ dự đoán chính xác số suất cần chuẩn bị cho từng line, giảm tình trạng “cháy line” và cải thiện trải nghiệm ăn trưa cho nhân viên.

[1]: https://pdfs.semanticscholar.org/c47b/35a83acec5cc522d8291033d11e741b59594.pdf?utm_source=chatgpt.com "[PDF] Demand Forecasting for Food Production Using Machine Learning ..."
[2]: https://dergipark.org.tr/en/pub/opusjsr/issue/91958/1649256?utm_source=chatgpt.com "Machine Learning Techniques for Cafeteria Demand Forecasting ..."
[3]: https://en.wikipedia.org/wiki/Demand_sensing?utm_source=chatgpt.com "Demand sensing"
[4]: https://arxiv.org/abs/1704.04110?utm_source=chatgpt.com "DeepAR: Probabilistic Forecasting with Autoregressive Recurrent Networks"
