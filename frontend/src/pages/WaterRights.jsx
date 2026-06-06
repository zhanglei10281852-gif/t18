import React, { useState, useEffect } from "react";
import { Table, Progress, Card, Spin, message } from "antd";
import api from "../api";

function WaterRights() {
  const [plots, setPlots] = useState([]);
  const [quotaData, setQuotaData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const plotsRes = await api.get("/api/plots");
      setPlots(plotsRes.data);

      const quotaPromises = plotsRes.data.map((plot) =>
        api.get(`/api/water/quota/${plot.id}`),
      );
      const results = await Promise.all(quotaPromises);
      setQuotaData(results.map((r) => r.data));
    } catch (error) {
      message.error("获取数据失败");
    }
    setLoading(false);
  };

  const columns = [
    {
      title: "地块编号",
      dataIndex: "plot_code",
      key: "plot_code",
    },
    {
      title: "年度配额(m³)",
      dataIndex: "annual_quota",
      key: "annual_quota",
      render: (v) => v?.toFixed(2),
      sorter: (a, b) => a.annual_quota - b.annual_quota,
    },
    {
      title: "已使用(m³)",
      dataIndex: "total_used",
      key: "total_used",
      render: (v) => v?.toFixed(2),
    },
    {
      title: "剩余(m³)",
      dataIndex: "remaining",
      key: "remaining",
      render: (v) => v?.toFixed(2),
    },
    {
      title: "使用进度",
      dataIndex: "usage_percent",
      key: "usage_percent",
      render: (v, record) => (
        <Progress
          percent={Math.round(v || 0)}
          status={v > 80 ? "exception" : v > 50 ? "active" : "normal"}
          style={{ maxWidth: 200 }}
        />
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  const totalQuota = quotaData.reduce((sum, q) => sum + q.annual_quota, 0);
  const totalUsed = quotaData.reduce((sum, q) => sum + q.total_used, 0);
  const totalRemaining = quotaData.reduce((sum, q) => sum + q.remaining, 0);

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginBottom: 24 }}>水权管理</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 16,
          marginBottom: 24,
        }}
      >
        <Card>
          <div style={{ fontSize: 14, color: "#666", marginBottom: 8 }}>
            年度总配额
          </div>
          <div style={{ fontSize: 28, fontWeight: "bold", color: "#1890ff" }}>
            {totalQuota.toFixed(2)} m³
          </div>
        </Card>
        <Card>
          <div style={{ fontSize: 14, color: "#666", marginBottom: 8 }}>
            已使用
          </div>
          <div style={{ fontSize: 28, fontWeight: "bold", color: "#faad14" }}>
            {totalUsed.toFixed(2)} m³
          </div>
        </Card>
        <Card>
          <div style={{ fontSize: 14, color: "#666", marginBottom: 8 }}>
            剩余配额
          </div>
          <div style={{ fontSize: 28, fontWeight: "bold", color: "#52c41a" }}>
            {totalRemaining.toFixed(2)} m³
          </div>
        </Card>
      </div>

      <Card title="各地块配额使用进度">
        <Table
          columns={columns}
          dataSource={quotaData}
          rowKey="plot_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}

export default WaterRights;
