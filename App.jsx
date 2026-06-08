import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [page, setPage] = useState("home");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState({ total: 0, safe: 0, violation: 0 });
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [filterDate, setFilterDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  const loadHistory = async () => {
    const res = await axios.get("http://127.0.0.1:8001/history");
    setHistory(res.data);
  };

  const loadStatistics = async () => {
    const res = await axios.get("http://127.0.0.1:8001/statistics");
    setStats(res.data);
  };

  useEffect(() => {
    loadHistory();
    loadStatistics();
  }, []);

  const handleChooseFile = (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
  };

  const handleDetectImage = async () => {
    if (!file) {
      alert("Vui lòng chọn ảnh trước");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8001/detect", formData);

      if (res.data.error) {
        alert(res.data.error);
      } else {
        setResult(res.data);
        await loadHistory();
        await loadStatistics();
      }
    } catch (error) {
      alert("Lỗi xử lý ảnh. Kiểm tra backend FastAPI.");
      console.log(error);
    }

    setLoading(false);
  };

  const deleteHistoryItem = async (id) => {
    if (!window.confirm("Bạn có chắc muốn xóa lịch sử này không?")) return;

    try {
      await axios.delete(`http://127.0.0.1:8001/history/${id}`);
      setSelectedHistory(null);
      await loadHistory();
      await loadStatistics();
    } catch (error) {
      alert("Lỗi khi xóa lịch sử");
      console.log(error);
    }
  };

  const deleteAllHistory = async () => {
    if (!window.confirm("Bạn có chắc muốn xóa toàn bộ lịch sử không?")) return;

    try {
      await axios.delete("http://127.0.0.1:8001/history");
      setSelectedHistory(null);
      await loadHistory();
      await loadStatistics();
    } catch (error) {
      alert("Lỗi khi xóa toàn bộ lịch sử");
      console.log(error);
    }
  };

  const safePercent =
    stats.total > 0 ? Math.round((stats.safe / stats.total) * 100) : 0;

  const violationPercent =
    stats.total > 0 ? Math.round((stats.violation / stats.total) * 100) : 0;

  const filteredHistory = history.filter((item) => {
  if (!filterDate && !startTime && !endTime) return true;

  const [datePart, timePart] = item.time.split(" ");
  const [day, month, year] = datePart.split("/");

  const itemDate = `${year}-${month}-${day}`;
  const itemTime = timePart;

  if (filterDate && itemDate !== filterDate) return false;
  if (startTime && itemTime < startTime) return false;
  if (endTime && itemTime > endTime) return false;

  return true;
});

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">
          <h2>🚦 Helmet AI</h2>
          <p>Detection System</p>
        </div>

        <button
          className={page === "home" ? "menu active" : "menu"}
          onClick={() => setPage("home")}
        >
          🏠 Trang chủ
        </button>

        <button
          className={page === "image" ? "menu active" : "menu"}
          onClick={() => setPage("image")}
        >
          📷 Kiểm tra ảnh
        </button>

        <button
          className={page === "history" ? "menu active" : "menu"}
          onClick={() => {
            setPage("history");
            loadHistory();
          }}
        >
          📁 Lịch sử
        </button>

        <button
          className={page === "stats" ? "menu active" : "menu"}
          onClick={() => {
            setPage("stats");
            loadStatistics();
          }}
        >
          📊 Thống kê
        </button>
      </aside>

      <main className="main">
        <header className="topbar">
          <h1>
            Hệ thống phát hiện người tham gia giao thông không đội mũ bảo hiểm
          </h1>
          <p>Ứng dụng YOLOv8 và Rule-Based trong giám sát giao thông</p>
        </header>

        {page === "home" && (
          <section>
            <div className="hero">
              <div>
                <h2>
                  Đội mũ bảo hiểm khi tham gia giao thông là trách nhiệm của mọi
                  người
                </h2>
                <p>
                  Hệ thống hỗ trợ phát hiện người đi xe máy không đội mũ bảo
                  hiểm, giúp nâng cao ý thức chấp hành luật giao thông.
                </p>
                <button onClick={() => setPage("image")}>
                  Bắt đầu kiểm tra
                </button>
              </div>
            </div>

            <div className="cards">
              <div className="card">
                <h3>🤖 AI Detection</h3>
                <p>Phát hiện người và mũ bảo hiểm bằng YOLOv8.</p>
              </div>

              <div className="card">
                <h3>⚙️ Rule-Based</h3>
                <p>Xác định an toàn hoặc vi phạm dựa trên vùng đầu.</p>
              </div>

              <div className="card">
                <h3>💾 SQLite</h3>
                <p>Lưu lịch sử nhận diện, trạng thái và kết quả xử lý.</p>
              </div>
            </div>
          </section>
        )}

        {page === "image" && (
          <section className="page-box">
            <h2>📷 Kiểm tra ảnh</h2>

            <input type="file" accept="image/*" onChange={handleChooseFile} />

            <button onClick={handleDetectImage} disabled={loading}>
              {loading ? "Đang xử lý..." : "Kiểm tra ảnh"}
            </button>

            {loading && <p className="loading">⏳ Đang nhận diện, vui lòng chờ...</p>}

            <div className="image-result">
              <div className="image-card">
                <h3>Ảnh gốc</h3>
                {preview ? (
                  <img src={preview} alt="preview" />
                ) : (
                  <p>Chưa chọn ảnh</p>
                )}
              </div>

              <div className="image-card">
                <h3>Kết quả</h3>
                {result ? (
                  <img src={result.result_image} alt="result" />
                ) : (
                  <p>Chưa có kết quả</p>
                )}
              </div>
            </div>

            {result && (
              <>
                <div className="result-info">
                  <div className="result-card safe-card">
                    <h3>✅ An toàn</h3>
                    <h1>{result.safe}</h1>
                  </div>

                  <div className="result-card danger-card">
                    <h3>🚫 Vi phạm</h3>
                    <h1>{result.violation}</h1>
                  </div>
                </div>

                <p className="process-time">
                  ⏱ Thời gian xử lý: {result.processing_time} giây
                </p>
              </>
            )}
          </section>
        )}

        {page === "history" && (
          <section className="page-box">
            <div className="history-top">
              <h2>📁 Lịch sử nhận diện</h2>

              {history.length > 0 && (
                <button className="delete-all-btn" onClick={deleteAllHistory}>
                  🧹 Xóa toàn bộ
                </button>
              )}
            </div>
            <div className="filter-box">
            <div>
              <label>Ngày</label>
              <input
                type="date"
                value={filterDate}
                onChange={(e) => setFilterDate(e.target.value)}
              />
            </div>

            <div>
              <label>Giờ bắt đầu</label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
              />
            </div>

            <div>
              <label>Giờ kết thúc</label>
              <input
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
              />
            </div>

            <button
              onClick={() => {
                setFilterDate("");
                setStartTime("");
                setEndTime("");
              }}
            >
              Làm mới
            </button>
          </div>

            {filteredHistory.length === 0 ? (
              <p>Chưa có dữ liệu</p>
            ) : (
              <div className="history-table">
                <table>
                  <thead>
                    <tr>
                      <th>STT</th>
                      <th>Tên file</th>
                      <th>Trạng thái</th>
                      <th>Thời gian</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredHistory.map((item, index) => (
                      <>
                        <tr
                          key={item.id}
                          className={
                            selectedHistory?.id === item.id ? "selected-row" : ""
                          }
                        >
                          <td>{index + 1}</td>

                          <td title={item.filename}>
                            {item.filename.length > 32
                              ? item.filename.substring(0, 32) + "..."
                              : item.filename}
                          </td>

                          <td>
                            <span
                              className={
                                item.status === "Vi phạm"
                                  ? "danger-text"
                                  : "safe-text"
                              }
                            >
                              {item.status}
                            </span>
                          </td>

                          <td>{item.time}</td>

                          <td>
                            <button
                              className="small-btn"
                              onClick={() =>
                                selectedHistory?.id === item.id
                                  ? setSelectedHistory(null)
                                  : setSelectedHistory(item)
                              }
                            >
                              {selectedHistory?.id === item.id ? "Ẩn" : "Xem"}
                            </button>

                            <button
                              className="small-btn delete-btn"
                              onClick={() => deleteHistoryItem(item.id)}
                            >
                              Xóa
                            </button>
                          </td>
                        </tr>

                        {selectedHistory?.id === item.id && (
                          <tr className="detail-row">
                            <td colSpan="5">
                              <div className="inline-history-detail">
                                <h3>🖼 Chi tiết kết quả</h3>

                                <p>
                                  <b>Tên file:</b> {item.filename}
                                </p>

                                <p>
                                  <b>Trạng thái:</b>{" "}
                                  <span
                                    className={
                                      item.status === "Vi phạm"
                                        ? "danger-text"
                                        : "safe-text"
                                    }
                                  >
                                    {item.status}
                                  </span>
                                </p>

                                <p>
                                  <b>Thời gian:</b> {item.time}
                                </p>

                                <img src={item.resultfile} alt="history-result" />

                                <br />

                                <button
                                  className="delete-large-btn"
                                  onClick={() => deleteHistoryItem(item.id)}
                                >
                                  🗑 Xóa kết quả này
                                </button>
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

        {page === "stats" && (
          <section className="page-box">
            <h2>📊 Dashboard thống kê hệ thống</h2>

            <div className="stats-box">
              <div className="stat-card">
                <h3>📂 Tổng lượt</h3>
                <p>{stats.total}</p>
              </div>

              <div className="stat-card safe-stat">
                <h3>✅ Không vi phạm</h3>
                <p>{stats.safe}</p>
              </div>

              <div className="stat-card danger-stat">
                <h3>🚫 Vi phạm</h3>
                <p>{stats.violation}</p>
              </div>
            </div>

            <div className="dashboard">
              <div className="chart-card">
                <h3>🥧 Tỷ lệ kết quả</h3>

                <div
                  className="pie-chart"
                  style={{
                    background: `conic-gradient(#2e7d32 0% ${safePercent}%, #c62828 ${safePercent}% 100%)`,
                  }}
                ></div>

                <div className="legend">
                  <span>✅ Không vi phạm: {safePercent}%</span>
                  <span>🚫 Vi phạm: {violationPercent}%</span>
                </div>
              </div>

              <div className="chart-card">
                <h3>📊 Biểu đồ cột</h3>

                <div className="bar-chart">
                  <div className="bar-group">
                    <div
                      className="bar safe-bar"
                      style={{
                        height:
                          stats.total > 0
                            ? `${(stats.safe / stats.total) * 220}px`
                            : "0px",
                      }}
                    ></div>
                    <p>Không vi phạm</p>
                    <b>{stats.safe}</b>
                  </div>

                  <div className="bar-group">
                    <div
                      className="bar danger-bar"
                      style={{
                        height:
                          stats.total > 0
                            ? `${(stats.violation / stats.total) * 220}px`
                            : "0px",
                      }}
                    ></div>
                    <p>Vi phạm</p>
                    <b>{stats.violation}</b>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;