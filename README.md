Hôm nay 22:00
person5_ar-20260928T145941Z-1-001.zip
Lưu trữ Zip
bây giờ người làm nhiệm vụ số 5 đã gửi bây giờ tôi có thể bắt đầu rồi đúng không
Hôm nay 6:51
person 6_var-20260928T235038Z-1-001.zip
Lưu trữ Zip
person4_nelson_siegel-20260928T235014Z-1-001.zip
Lưu trữ Zip
person5_ar-20260928T234954Z-1-001.zip
Lưu trữ Zip
kiểm tra 3 file trên oke chưa
phần 6 lấy forecast nào nhiều forecast quá
của người 6
phần 6 nữa nè
của người 5 gồm 2 output việt nam với mỸ LẬN
chỉ từng bước cách đưa data vào thư mục data
Đã dán mã (1)(5).py
Python
nè sửa hết luôn 1 lần luôn đi
Dm Test Results
Dm Test VAR Vs VARMacro
Forecast Comparison RW AR
Forecast Comparison RW AR VAR VARMacro
Forecast Comparison VAR Vs VARMacro
Random Walk Forecasts
gửi đủ chương giờ viết các phần phân tích kết quả, phương pháp cho phần 7 
Đã dán mã (1)(6).py
Python
nè sửa hết lại đi
Đã dán mã (1)(7).py
Python
nè sửa lại dm_test.py luôn
file forecast của người 6 nè là horizon =1 đúng không
Us Ns Maturity Error Stats
Us Pca Benchmark Components
Vietnam Ns Maturity Error Stats
đây là 3 ouputs của người 4 bây giờ tôi sẽ chạy ar( phần của người 5) cho horizon 3,6,12
person5_ar_forecast.py
Python
person5_ar_forecast.R
Tệp
này file code của người 5
Ar Yield Forecasts With Actuals All Horizons
nè tự coi i
Nguoi6_VAR_IRF.R
Tệp
file code của người 6 nè
Văn bản đã dán (1).txt
Tài liệu
sửa lại hết dùm đi
person5_ar_forecast(1).R
Tệp
trước khi qua person 7 thì tôi mới thấy trong phần của người 5 ngoài file python ra còn 1 file R nữa.. có ảnh hưởng gì k
Ar Yield Forecasts With Actuals All Horizons(1)
Ar Yield Forecasts With Actuals
nè coi đi năn nỉ
đây cấu trúc như này tạo folder mới data_all đó
Đã dán mã (1)(8).py
Python
nè sửa evaluation.py đi
👀
Văn bản đã dán (1)(1).txt
Tài liệu
Đã dán mã (1)(9).py
Python
nè code ban đầu nè sửa lại đi
Văn bản đã dán (1)(2).txt
Tài liệu
Văn bản đã dán (1)(3).txt
Tài liệu

Ừ. Mình vừa review lại toàn bộ logic chuyển từ h = 1 sang h = 1, 3, 6, 12, gồm code AR, VAR/VAR+Macro, evaluation và DM test. Kết luận là: cách mở rộng về cơ bản là đúng và nhất quán, nhưng có vài điểm quan trọng cần hiểu rõ.

1. Trước đây h = 1 làm thế nào?

Với h = 1:

Origin t
   ↓
dự báo t+1
   ↓
so sánh với actual t+1

AR cũ dùng expanding window và chọn lag bằng BIC. Khi mình mở rộng, h = 1 vẫn giữ nguyên logic đó. Thậm chí mình đã đối chiếu AR cũ và AR mới: kết quả h=1 trùng nhau.

Code mới của AR lấy:

origin = target - horizon

rồi chỉ dùng dữ liệu:

t ≤ origin

để dự báo.

2. Khi chuyển sang h = 3, 6, 12 thì mình đã thay đổi gì?

Điểm quan trọng nhất là không lấy forecast h=1 rồi kéo dài ra một cách đơn giản.

Ví dụ h=3:

Origin:       Jan 2024
                ↓
             forecast
                ↓
Feb → Mar → Apr
             ↑
        lấy forecast tháng Apr

Tức là:

origin = target − 3 tháng

Sau đó mô hình chỉ được sử dụng thông tin đến origin và dự báo 3 bước về phía trước.

VAR được code đúng theo logic:

Fit VAR tại origin → predict(n.ahead = h) → lấy dòng thứ h.

Điều này rất quan trọng vì nó tránh look-ahead bias / data leakage.

3. AR đã được mở rộng đúng kiểu recursive forecast

AR mới cũng làm tương tự.

Ví dụ h=6:

Origin
 ↓
AR( p )
 ↓
t+1
 ↓
t+2
 ↓
t+3
 ↓
t+4
 ↓
t+5
 ↓
t+6 ← forecast dùng để đánh giá

Các giá trị dự báo trung gian được đưa ngược trở lại làm đầu vào cho bước tiếp theo.

Code thực hiện:

for _ in range(horizon):
    ...
    next_value = coef @ x
    history.append(next_value)

Vì vậy h=12 thực sự là forecast 12 bước, chứ không phải 12 lần dự báo một bước độc lập.

4. VAR và VAR+Macro cũng làm đúng nguyên tắc

Đây là điểm mình kiểm tra kỹ nhất.

Với mỗi:

h = 1
h = 3
h = 6
h = 12

và mỗi target, code tính:

origin = target - h

Sau đó:

data ≤ origin
       ↓
fit VAR
       ↓
predict n.ahead = h
       ↓
lấy forecast tại bước h

Do đó không có chuyện mô hình h=12 nhìn thấy dữ liệu từ 2024 khi origin nằm trước 2024.

5. Một điểm rất tốt: h=1 vẫn được giữ nguyên

Đây là điều mình đánh giá quan trọng nhất.

Sau khi chuyển sang multi-horizon, chúng ta không bỏ benchmark cũ.

Ta có:

AR cũ h=1
        ↓
AR mới h=1

và hai kết quả forecast h=1 đã được đối chiếu:

72/72 quan sát trùng nhau, forecast_yield giống nhau.

Nên việc mở rộng sang:

h = 1, 3, 6, 12

không làm thay đổi benchmark h=1 ban đầu.

6. Random Walk cũng đã được mở rộng đúng

RW hơi khác AR/VAR.

Với h=3 chẳng hạn:

Origin
   ↓
RW forecast
   ↓
giữ nguyên yield tại Origin
   ↓
so sánh với actual tại Origin + 3 tháng

Tức:

$$ \hat y_{t+3|t}=y_t $$

Chứ không phải lấy forecast của tháng t+1 rồi tiếp tục forecast.

Đây là benchmark Random Walk phù hợp cho multi-step.

Evaluation cũng tạo đủ:

4 horizons × 24 targets × 3 maturities
= 288 forecasts

cho RW.

7. Phần evaluation cũng đã chuyển đúng

Bây giờ evaluation không còn:

HORIZONS = [1]

mà là:

HORIZONS = [1, 3, 6, 12]

và:

MATURITIES = [12, 24, 120]

tức:

             1Y    2Y    10Y
           ┌────┬────┬─────┐
h = 1      │    │    │     │
h = 3      │    │    │     │
h = 6      │    │    │     │
h = 12     │    │    │     │
           └────┴────┴─────┘

4 model × 4 horizon × 3 maturity.

Code cũng kiểm tra duplicate theo:

model
horizon
target
maturity

trước khi tính metrics.

Đây là một check tốt.

8. DM test cũng đã được sửa cho multi-horizon

Đây là phần rất quan trọng.

Nếu h=1 thì DM dùng:

HAC lag = 0

Nhưng khi h=3:

HAC lag = 2

h=6:

HAC lag = 5

h=12:

HAC lag = 11

Code hiện tại dùng:

max_lag = max(h - 1, 0)

Điều này phù hợp với cách xử lý dependence của multi-step forecast errors trong implementation hiện tại.

9. Nhưng có một điểm cần đặc biệt lưu ý

Đây là chỗ làm kết quả h=3, 6, 12 rối hơn h=1.

Khi h tăng, số bước forecast tăng:

h=1   → 1 bước
h=3   → 3 bước
h=6   → 6 bước
h=12  → 12 bước

Đối với AR và VAR, forecast càng xa thì forecast uncertainty và sai số tích lũy càng lớn.

Đặc biệt với VAR, mỗi bước dự báo lại phụ thuộc vào trạng thái dự báo trước đó.

Do đó:

h=1
↓
mô hình còn bám khá sát dữ liệu

h=12
↓
nhiều bước recursive
↓
sai số tích lũy
↓
forecast có thể lệch xa actual

Vì vậy việc bảng h=12 nhìn “xấu” hoặc phân tán hơn không phải dấu hiệu tự động của lỗi code.

10. Có một vấn đề dữ liệu mà chúng ta đã xử lý

VAR+Macro chỉ có:

285 observations

thay vì:

288 observations

trong tổng bộ forecast.

Nguyên nhân là một số forecast VAR5 ở cuối mẫu không có đủ dữ liệu theo cấu trúc ban đầu.

Quan trọng là evaluation không tự ý điền 0.

Nó giữ lại các quan sát hợp lệ.

Kết quả:

AR          288
VAR         288
VAR+Macro   285
RW          288

Và h=1 VAR+Macro có 23 quan sát/maturity thay vì 24.

Đây là điều cần ghi rõ trong báo cáo.

11. Một điểm mình muốn chỉnh cách hiểu trước đó

Lúc đầu nhìn bảng kết quả, mình nói kiểu:

“horizon càng dài thì kết quả càng rối.”

Câu này đúng về hình thức kết quả, nhưng về mặt học thuật nên nói chính xác hơn:

Khi horizon tăng, sai số dự báo và sự khác biệt giữa các mô hình thay đổi đáng kể; do đó hiệu quả tương đối của các mô hình trở nên phụ thuộc nhiều hơn vào horizon và maturity.

Không nên nói đơn giản:

“horizon càng dài thì mô hình càng tệ.”

Vì bảng của mình không cho thấy điều đó cho tất cả mô hình.

Ví dụ AR 10Y:

h=1   MAE = 0.1898
h=3   MAE = 0.3160
h=6   MAE = 0.2190
h=12  MAE = 0.4120

Có tăng, nhưng không tăng đều theo từng horizon.

12. Có một điều rất đáng yên tâm: kết quả hiện tại có logic kinh tế/thống kê

Khi nhìn toàn bộ pipeline:

Nelson–Siegel
      ↓
Level / Slope / Curvature
      ↓
 ┌───────────────┐
 │               │
AR              VAR
 │               │
 └──────┬────────┘
        ↓
     VAR+Macro
        ↓
 Forecast
 h=1,3,6,12
        ↓
  RW benchmark
        ↓
 MAE / RMSE
        ↓
 Diebold-Mariano

thì logic của pipeline hiện tại là nhất quán.

Đặc biệt:

AR multi-step: recursive.
VAR multi-step: recursive n.ahead.
VAR+Macro: dự báo đồng thời macro và factors trong VAR.
RW: giữ giá trị tại origin.
Actual: dùng chung cho các model.
MAE/RMSE: tính trên forecast–actual.
DM: so sánh loss trên cùng observations.
h được đưa vào HAC lag.

Đây là cấu trúc mà mình sẽ giữ lại.

13. Tuy nhiên, nếu chuẩn bị nộp bài thì mình sẽ kiểm tra thêm 3 thứ

Có 3 check cuối cùng mình khuyên nên làm trước khi nhóm chốt kết quả:

Check 1 — Forecast origin

Kiểm tra ngẫu nhiên:

h=1  → origin = target - 1
h=3  → origin = target - 3
h=6  → origin = target - 6
h=12 → origin = target - 12

Để chắc chắn tuyệt đối không có leakage.

Check 2 — AR h=3/6/12

Đối chiếu một vài forecast thủ công:

origin
→ AR forecast step 1
→ step 2
→ ...
→ step h

để chắc chắn forecast cuối cùng thực sự là h-step recursive forecast.

Check 3 — DM

Đây là check quan trọng nhất về mặt thống kê.

Hiện tại nhóm đang chạy 72 DM tests:

$$ 6\ comparisons \times 4\ horizons \times 3\ maturities=72 $$

nên khi báo cáo các p-value < 0.05, cần ghi chú rằng đây là nhiều kiểm định, và chưa áp dụng hiệu chỉnh multiple comparisons.

Kết luận review

Mình chưa thấy lỗi logic nghiêm trọng trong quá trình chuyển từ h=1 → h=1,3,6,12.

Thay đổi quan trọng nhất là:

Không phải “chạy lại h=1 nhiều lần”, mà đã chuyển sang đúng multi-step out-of-sample forecasting với origin = target − h.

Và việc h=3, 6, 12 cho kết quả phức tạp hơn h=1 là điều có thể xảy ra và bản thân nó không phải dấu hiệu code sai.

Nếu nhóm muốn làm chắc trước khi viết luận văn, bước tiếp theo mình sẽ review riêng 3 file forecast gốc (AR, VAR3, VAR5) và kiểm tra trực tiếp 1–2 dòng của h=3, h=6, h=12 để xác nhận không có leakage. Đây là check đáng làm nhất trước khi tin hoàn toàn vào bảng MAE/RMSE và DM.

Hôm nay 10:48
giờ tôi muốn làm cái gọn lại lại để up lên git hub chỉ tôi xóa những cái k cần thiết
👍

Đúng, nhìn folder hiện tại thì đang bị trộn giữa bộ cũ h=1 và bộ mới multi-horizon h=1,3,6,12. Nếu mục tiêu là up GitHub cho gọn và dễ hiểu, mình khuyên dọn như sau.

1. Cấu trúc cuối cùng nên giữ
person7/
│
├── code/
│   ├── evaluation.py
│   └── dm_test.py
│
├── data/
│   └── README.txt
│
├── data_all/
│   ├── ar_yield_forecasts_with_actuals_all_horizons.csv
│   ├── us_monthly_master_with_ns.csv
│   ├── us_monthly_observed_yields_2024_2025.csv
│   ├── VAR3_yield_forecasts_all_horizons.csv
│   └── VAR5_yield_forecasts_all_horizons.csv
│
├── results/
│   ├── all_forecasts_multi_horizon.csv
│   ├── forecast_metrics_multi_horizon.csv
│   ├── forecast_comparison_multi_horizon_wide.csv
│   ├── forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv
│   ├── random_walk_forecasts_all_horizons.csv
│   ├── dm_test_results_all_horizons.csv
│   └── dm_test_VAR_vs_VARMacro_all_horizons.csv
│
└── README.md
2. Trong data/ → XÓA

Folder data hiện tại là bộ cũ h=1, không cần cho pipeline cuối nữa.

Bạn có:

data/
├── ar_yield_forecasts_with_actuals.csv
├── us_monthly_master_with_ns.csv
├── var3_yield_forecasts_common_window.csv
└── var5_yield_forecasts_common_window.csv

👉 XÓA TOÀN BỘ 4 FILE NÀY.

Vì bộ multi-horizon hiện tại đã nằm trong:

data_all/

Đặc biệt đừng nhầm:

data/us_monthly_master_with_ns.csv

với:

data_all/us_monthly_master_with_ns.csv

Giữ cái trong data_all, xóa cái trong data.

3. data_all/ → GIỮ NGUYÊN

Đây là bộ dữ liệu đầu vào chính của phiên bản cuối.

Giữ:

ar_yield_forecasts_with_actuals_all_horizons.csv
us_monthly_master_with_ns.csv
us_monthly_observed_yields_2024_2025.csv
VAR3_yield_forecasts_all_horizons.csv
VAR5_yield_forecasts_all_horizons.csv

Không xóa.

Evaluation hiện tại sử dụng các file này. Code evaluation đọc AR, VAR, VAR+Macro từ data_all và xây Random Walk từ yield master/actuals.

4. results/ → XÓA các file cũ

Trong screenshot bạn có:

❌ XÓA
dm_test_results.csv
dm_test_VAR_vs_VARMacro.csv
forecast_comparison_Rw_AR_VAR_VARMacro.csv
forecast_comparison_VAR_vs_VARMacro.csv
random_walk_forecasts.csv

Đây là các output bộ cũ h=1.

5. results/ → GIỮ các file này
✅ GIỮ
all_forecasts_multi_horizon.csv

forecast_metrics_multi_horizon.csv

forecast_comparison_multi_horizon_wide.csv

forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv

random_walk_forecasts_all_horizons.csv

dm_test_results_all_horizons.csv

dm_test_VAR_vs_VARMacro_all_horizons.csv

Đây là bộ kết quả cuối:

h = 1
h = 3
h = 6
h = 12

với:

1Y
2Y
10Y
6. code/ → CHỈ GIỮ 2 file

Screenshot hiện tại:

code/
├── dm_test.py
└── evaluation.py

👉 Giữ cả 2.

Nhưng có một việc cực kỳ quan trọng trước khi upload:

Mở evaluation.py, kiểm tra có:

HORIZONS = [1, 3, 6, 12]

và mở dm_test.py, kiểm tra cũng có:

HORIZONS = [1, 3, 6, 12]

Nếu có → đây chính là code final → giữ.

Nếu một trong hai vẫn là code cũ:

HORIZONS = [1]

thì đừng xóa file multi-horizon cũ vội, mà phải thay thế bằng bản multi-horizon trước.

7. README.txt

Có:

README.txt

👉 Giữ lại, nhưng mình khuyên đổi tên thành:

README.md

GitHub sẽ hiển thị Markdown đẹp hơn.

8. Sau khi dọn, folder sẽ cực kỳ gọn
person7/
│
├── code/
│   ├── evaluation.py
│   └── dm_test.py
│
├── data_all/
│   ├── ar_yield_forecasts_with_actuals_all_horizons.csv
│   ├── us_monthly_master_with_ns.csv
│   ├── us_monthly_observed_yields_2024_2025.csv
│   ├── VAR3_yield_forecasts_all_horizons.csv
│   └── VAR5_yield_forecasts_all_horizons.csv
│
├── results/
│   ├── all_forecasts_multi_horizon.csv
│   ├── forecast_metrics_multi_horizon.csv
│   ├── forecast_comparison_multi_horizon_wide.csv
│   ├── forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv
│   ├── random_walk_forecasts_all_horizons.csv
│   ├── dm_test_results_all_horizons.csv
│   └── dm_test_VAR_vs_VARMacro_all_horizons.csv
│
└── README.md
9. Tóm lại: thao tác ngay trên VS Code
Xóa folder:
data/
Trong results/, xóa:
dm_test_results.csv
dm_test_VAR_vs_VARMacro.csv
forecast_comparison_Rw_AR_VAR_VARMacro.csv
forecast_comparison_VAR_vs_VARMacro.csv
random_walk_forecasts.csv
Giữ:
code/
data_all/
results/  ← chỉ giữ 7 file multi-horizon
README.txt

Đừng xóa data_all hay các file _all_horizons.csv.

Một lưu ý quan trọng trước khi bạn xóa

Mình muốn bạn chưa bấm xóa ngay. Hãy mở evaluation.py và dm_test.py, chụp cho mình phần đầu code khoảng 30–50 dòng.

Mình sẽ kiểm tra xem 2 file này hiện tại có thực sự là bản multi-horizon cuối cùng không. Nếu đúng, mình sẽ chỉ bạn xóa từng file một và sau đó mình có thể giúp bạn làm luôn README.md chuẩn để push GitHub.

phải yên tâm, giờ chỉ viết lại cái README ĐI do cái đó chưa sửa

Đây là README.md bản mới, đã cập nhật theo đúng pipeline cuối cùng h = 1, 3, 6, 12, gồm RW, AR, VAR, VAR+Macro, MAE/RMSE và DM test.

📄 Tải README.md

Bạn chỉ cần đổi README.txt cũ thành/xóa nó và đặt file này vào thư mục person7:

person7/
├── code/
├── data_all/
├── results/
└── README.md

README này cũng đã ghi rõ cách chạy:

python code/evaluation.py
python code/dm_test.py

và giải thích luôn ý nghĩa DM âm/dương, để sau này người khác vào GitHub đọc code không bị nhầm dấu như lúc mình phân tích ban đầu. 

README.md
Tài liệu

Thư viện
/
README.md
Person 7 – Forecast Evaluation
1. Overview

This folder contains the out-of-sample evaluation of four models for forecasting the U.S. Treasury yield curve:

Random Walk (RW)
AR
VAR using the Nelson–Siegel factors: Level, Slope and Curvature
VAR+Macro using Level, Slope, Curvature, U.S. inflation and the U.S. policy rate

The evaluation is performed for three Treasury maturities:

1Y (DGS1)
2Y (DGS2)
10Y (DGS10)

and four forecast horizons:

1 month
3 months
6 months
12 months

The evaluation period is January 2024 – December 2025.

2. Folder Structure
person7/
├── code/
│   ├── evaluation.py
│   └── dm_test.py
├── data_all/
│   ├── ar_yield_forecasts_with_actuals_all_horizons.csv
│   ├── us_monthly_master_with_ns.csv
│   ├── us_monthly_observed_yields_2024_2025.csv
│   ├── VAR3_yield_forecasts_all_horizons.csv
│   └── VAR5_yield_forecasts_all_horizons.csv
├── results/
│   ├── all_forecasts_multi_horizon.csv
│   ├── forecast_metrics_multi_horizon.csv
│   ├── forecast_comparison_multi_horizon_wide.csv
│   ├── forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv
│   ├── random_walk_forecasts_all_horizons.csv
│   ├── dm_test_results_all_horizons.csv
│   └── dm_test_VAR_vs_VARMacro_all_horizons.csv
└── README.md
3. Forecast Evaluation Method

The target period is:

2024-01-31 → 2025-12-31

For each forecast horizon h, the forecast origin is:

origin = target date − h months

Only information available up to the forecast origin is used.

For example, for a 3-month forecast:

Origin → t+1 → t+2 → t+3
                    ↑
              forecast evaluated

This procedure is applied to:

h = 1, 3, 6, 12
4. Models
4.1 Random Walk

Random Walk is the benchmark:

ŷ(t+h|t) = y(t)

The yield at the forecast origin is used as the forecast for the future horizon.

4.2 AR

The AR model forecasts the three Nelson–Siegel factors individually:

Level
Slope
Curvature

The AR lag is selected using BIC, with candidate lags from 1 to 6.

For horizons greater than one month, forecasts are generated recursively.

4.3 VAR

The VAR model contains:

Level
Slope
Curvature

The VAR lag is selected using BIC, with maximum lag 6.

For each forecast origin, the model is estimated using information available up to that origin and the forecast corresponding to the required horizon is retained.

4.4 VAR+Macro

The extended VAR model contains:

Level
Slope
Curvature
Inflation
Policy Rate

The lag is selected using BIC. The macro variables are forecast jointly with the yield-curve factors when producing multi-step forecasts.

5. From Factors to Treasury Yields

Forecasted Nelson–Siegel factors are converted into predicted yields for:

1Y, 2Y, 10Y

using the same Nelson–Siegel specification and lambda.

The predicted yields are then compared with observed Treasury yields.

6. Evaluation Metrics
MAE – Mean Absolute Error
MAE = mean(|actual − forecast|)

MAE measures the average absolute forecasting error.

RMSE – Root Mean Squared Error
RMSE = sqrt(mean((actual − forecast)^2))

RMSE gives greater weight to larger errors.

For both measures:

Lower values indicate smaller forecast errors.

7. Diebold–Mariano Test

The Diebold–Mariano (DM) test compares the predictive accuracy of two models.

The loss function is squared error:

Loss = error²

The loss differential is:

dₜ = Loss(model 1) − Loss(model 2)

Therefore:

DM > 0: model 2 has lower average loss than model 1.
DM < 0: model 1 has lower average loss than model 2.

For multi-step forecasts, the implementation uses HAC/Newey–West-style long-run variance with:

max_lag = h − 1

The test is two-sided.

The following model pairs are tested:

RW vs AR
RW vs VAR
RW vs VAR+Macro
AR vs VAR
AR vs VAR+Macro
VAR vs VAR+Macro

across all four horizons and three maturities.

8. Results

The main outputs are stored in results/.

Forecast accuracy

forecast_metrics_multi_horizon.csv

Contains model, horizon, maturity, number of observations, MAE and RMSE.

Wide comparison

forecast_comparison_multi_horizon_wide.csv

Provides a wider comparison across models, horizons and maturities.

VAR vs VAR+Macro

forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv

Provides the direct comparison between VAR and VAR+Macro.

Diebold–Mariano

dm_test_results_all_horizons.csv

Contains DM results for all model pairs.

dm_test_VAR_vs_VARMacro_all_horizons.csv

Contains the specific VAR versus VAR+Macro comparison.

9. Main Empirical Findings

Forecasting performance varies with both forecast horizon and Treasury maturity.

The results do not show a single forecasting performance pattern across:

h = 1, 3, 6, 12

and:

1Y, 2Y, 10Y

In particular, adding inflation and the policy rate to VAR does not produce a uniform improvement in out-of-sample forecast accuracy relative to VAR using only Level, Slope and Curvature.

Most VAR versus VAR+Macro DM comparisons do not show a statistically significant difference at the 5% level. Significant differences occur for the 10-year maturity at:

6-month horizon: DM = -2.6057, p = 0.0092
12-month horizon: DM = -2.3980, p = 0.0165

Because the statistic is defined as:

Loss(VAR) − Loss(VAR+Macro)

the negative statistics indicate lower squared-error loss for VAR than VAR+Macro in these two cases.

At the 12-month horizon and 2-year maturity:

DM = -1.7454
p = 0.0809

which does not reach the 5% significance level.

These results are out-of-sample forecasting evidence and should not be interpreted as evidence of a causal relationship between macroeconomic variables and the yield curve.

10. Reproducibility

Run the forecast evaluation from the person7 folder:

python code/evaluation.py

Then run the Diebold–Mariano tests:

python code/dm_test.py

The scripts read the files in:

data_all/

and save the results to:

results/
11. Important Notes
Evaluation period: January 2024 – December 2025.
Forecast horizons: 1, 3, 6 and 12 months.
Maturities: 1Y, 2Y and 10Y.
VAR+Macro has fewer available observations in some cases because of missing end-of-sample macro-related observations in the original forecast output.
Missing observations are not replaced with zero.
Forecast accuracy is evaluated separately from the dynamic relationship between macro variables and yield-curve factors.
IRF analysis is separate from this forecasting evaluation.