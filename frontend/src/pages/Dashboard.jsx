import React, { useState, useEffect } from "react";
import { Card, Row, Col, Progress, Statistic, Tag, Empty, Spin } from "antd";
import {
  CloudOutlined,
  DatabaseOutlined,
  FundOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import api from "../api";
import { useAuth } from "../context/AuthContext";

const cropNames = {
  rice: "水稻",
  wheat: "小麦",
  corn: "玉米",
  cotton: "棉花",
};

const urgencyText = {
  no_need: "无需灌溉",
  normal: "正常",
  suggested: "建议灌溉",
  urgent: "急需灌溉",
};

const urgencyColor = {
  no_need: "green",
  normal: "blue",
  suggested: "gold",
  urgent: "red",
};

function Dashboard() {
  const [suggestions, setSuggestions] = useState([]);
  const [quotaData, setQuotaData] = useState([]);
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, hasRole } = useAuth();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sugRes, weatherRes, plotsRes] = await Promise.all([
        api.get("/api/irrigation/suggestions/today"),
        api.get("/api/weather", { params: { limit: 1 } }),
        api.get("/api/plots"),
      ]);
      setSuggestions(sugRes.data);
      if (weatherRes.data.length > 0) {
        setWeather(weatherRes.data[0]);
      }

      const quotaPromises = plotsRes.data
        .slice(0, 8)
        .map((plot) => api.get(`/api/water/quota/${plot.id}`));
      const quotaResults = await Promise.all(quotaPromises);
      setQuotaData(quotaResults.map((r) => r.data));
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    }
    setLoading(false);
  };

  const stats = {
    totalPlots: quotaData.length,
    needIrrigation: suggestions.filter(
      (s) => s.urgency_level === "urgent" || s.urgency_level === "suggested",
    ).length,
    totalQuota: quotaData.reduce((sum, q) => sum + q.annual_quota, 0),
    totalUsed: quotaData.reduce((sum, q) => sum + q.total_used, 0),
  };

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="地块总数"
              value={stats.totalPlots}
              prefix={<DatabaseOutlined style={{ color: "#1890ff" }} />}
              suffix="块"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="需灌溉地块"
              value={stats.needIrrigation}
              prefix={<WarningOutlined style={{ color: "#faad14" }} />}
              suffix="块"
              valueStyle={{
                color: stats.needIrrigation > 0 ? "#faad14" : "#52c41a",
              }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="年度总配额"
              value={stats.totalQuota.toFixed(0)}
              prefix={<FundOutlined style={{ color: "#52c41a" }} />}
              suffix="m³"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="已用水量"
              value={stats.totalUsed.toFixed(0)}
              prefix={<CloudOutlined style={{ color: "#722ed1" }} />}
              suffix="m³"
            />
          </Card>
        </Col>
      </Row>

      {weather && (
        <Card title="今日气象" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="平均气温"
                value={weather.temperature_avg}
                suffix="℃"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="最高气温"
                value={weather.temperature_max}
                suffix="℃"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="最低气温"
                value={weather.temperature_min}
                suffix="℃"
              />
            </Col>
            <Col span={6}>
              <Statistic title="降雨量" value={weather.rainfall} suffix="mm" />
            </Col>
          </Row>
        </Card>
      )}

      <Card title="今日灌溉建议" style={{ marginBottom: 24 }}>
        {suggestions.length === 0 ? (
          <Empty description="暂无灌溉建议" />
        ) : (
          <Row gutter={[16, 16]}>
            {suggestions.map((s) => (
              <Col xs={24} sm={12} md={8} lg={6} key={s.id}>
                <Card
                  size="small"
                  className={`irrigation-card-${s.urgency_level}`}
                  title={
                    <span>
                      {s.plot?.plot_code || "未知地块"}
                      <Tag
                        color={urgencyColor[s.urgency_level]}
                        style={{ marginLeft: 8 }}
                      >
                        {urgencyText[s.urgency_level]}
                      </Tag>
                    </span>
                  }
                  style={{
                    borderLeft: `4px solid ${
                      s.urgency_level === "no_need"
                        ? "#52c41a"
                        : s.urgency_level === "urgent"
                          ? "#ff4d4f"
                          : s.urgency_level === "suggested"
                            ? "#faad14"
                            : "#1890ff"
                    }`,
                  }}
                >
                  <p style={{ margin: "4px 0", fontSize: 13, color: "#666" }}>
                    作物:{" "}
                    {s.plot
                      ? cropNames[s.plot.crop_type] || s.plot.crop_type
                      : "-"}
                  </p>
                  <p style={{ margin: "4px 0", fontSize: 13, color: "#666" }}>
                    面积: {s.plot?.area_mu || 0} 亩
                  </p>
                  <p style={{ margin: "4px 0", fontSize: 13, color: "#666" }}>
                    ETc: {s.etc?.toFixed(2) || 0} mm
                  </p>
                  <p style={{ margin: "4px 0", fontSize: 13, color: "#666" }}>
                    有效降雨: {s.effective_rainfall?.toFixed(2) || 0} mm
                  </p>
                  <p
                    style={{
                      margin: "4px 0",
                      fontSize: 13,
                      fontWeight: "bold",
                    }}
                  >
                    建议灌水量: {s.suggested_water_total?.toFixed(2) || 0} m³
                  </p>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Card>

      <Card title="本月用水量 vs 配额进度">
        {quotaData.length === 0 ? (
          <Empty description="暂无数据" />
        ) : (
          <Row gutter={[16, 16]}>
            {quotaData.map((q) => {
              const monthlyQuota = q.annual_quota / 12;
              const percent = Math.min(
                100,
                (q.total_used / q.annual_quota) * 100,
              );
              return (
                <Col xs={24} sm={12} md={8} lg={6} key={q.plot_id}>
                  <Card size="small" title={q.plot_code}>
                    <Progress
                      percent={Math.round(percent)}
                      status={
                        percent > 80
                          ? "exception"
                          : percent > 50
                            ? "active"
                            : "normal"
                      }
                    />
                    <p style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
                      已用: {q.total_used.toFixed(1)} /{" "}
                      {q.annual_quota.toFixed(1)} m³
                    </p>
                  </Card>
                </Col>
              );
            })}
          </Row>
        )}
      </Card>
    </div>
  );
}

export default Dashboard;
