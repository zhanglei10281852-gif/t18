import React, { useState, useEffect } from "react";
import { Card, Table, Tabs, Spin, message, Row, Col, Statistic } from "antd";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
} from "recharts";
import api from "../api";
import { useAuth } from "../context/AuthContext";

const cropNames = {
  rice: "水稻",
  wheat: "小麦",
  corn: "玉米",
  cotton: "棉花",
};

function Stats() {
  const [monthlyStats, setMonthlyStats] = useState([]);
  const [savingTrend, setSavingTrend] = useState([]);
  const [waterBills, setWaterBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const { hasRole } = useAuth();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, trendRes, billsRes] = await Promise.all([
        api.get("/api/water/usage/monthly"),
        api.get("/api/water/stats/saving-rate-trend", {
          params: { months: 6 },
        }),
        api.get("/api/water/stats/water-bills"),
      ]);
      setMonthlyStats(statsRes.data);
      setSavingTrend(trendRes.data);
      setWaterBills(billsRes.data);
    } catch (error) {
      message.error("获取统计数据失败");
    }
    setLoading(false);
  };

  const monthlyChartData = monthlyStats
    .reduce((acc, item) => {
      const key = `${item.year}-${String(item.month).padStart(2, "0")}`;
      const existing = acc.find((d) => d.month === key);
      if (existing) {
        existing.planned += item.planned_usage;
        existing.actual += item.actual_usage;
      } else {
        acc.push({
          month: key,
          planned: item.planned_usage,
          actual: item.actual_usage,
        });
      }
      return acc;
    }, [])
    .sort((a, b) => a.month.localeCompare(b.month));

  const perPlotMonthlyData = monthlyStats.reduce((acc, item) => {
    const key = item.plot_code;
    if (!acc[key]) {
      acc[key] = { plot: key, ...{} };
    }
    const monthKey = `${item.month}月`;
    acc[key][monthKey] = item.actual_usage;
    return acc;
  }, {});

  const perPlotChartData = Object.values(perPlotMonthlyData);

  const billColumns = [
    {
      title: "地块编号",
      dataIndex: "plot_code",
      key: "plot_code",
    },
    {
      title: "作物类型",
      dataIndex: "crop_type",
      key: "crop_type",
      render: (v) => cropNames[v] || v,
    },
    {
      title: "年度配额(m³)",
      dataIndex: "annual_quota",
      key: "annual_quota",
      render: (v) => v?.toFixed(2),
    },
    {
      title: "总用水量(m³)",
      dataIndex: "total_usage",
      key: "total_usage",
      render: (v) => v?.toFixed(2),
    },
    {
      title: "水费(元)",
      dataIndex: "total_fee",
      key: "total_fee",
      render: (v) => (
        <span style={{ color: "#faad14", fontWeight: "bold" }}>
          ¥{v?.toFixed(2)}
        </span>
      ),
    },
  ];

  const totalFee = waterBills.reduce((sum, b) => sum + (b.total_fee || 0), 0);
  const totalUsage = waterBills.reduce(
    (sum, b) => sum + (b.total_usage || 0),
    0,
  );

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginBottom: 24 }}>统计分析</h2>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="年度总水费"
              value={totalFee}
              precision={2}
              prefix="¥"
              valueStyle={{ color: "#faad14" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="年度总用水量"
              value={totalUsage}
              precision={2}
              suffix="m³"
              valueStyle={{ color: "#1890ff" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="地块数量"
              value={waterBills.length}
              suffix="块"
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="各地块月度用水对比" style={{ marginBottom: 24 }}>
        <div style={{ height: 350 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={perPlotChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="plot" />
              <YAxis />
              <Tooltip />
              <Legend />
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((m) => (
                <Bar key={m} dataKey={`${m}月`} name={`${m}月`} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card title="灌区节水率趋势" style={{ marginBottom: 24 }}>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={savingTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="saving_rate"
                name="节水率(%)"
                stroke="#52c41a"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="actual_usage"
                name="实际用水量(m³)"
                stroke="#1890ff"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card title="月度计划 vs 实际用水">
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthlyChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="planned" name="计划用水量(m³)" fill="#1890ff" />
              <Bar dataKey="actual" name="实际用水量(m³)" fill="#faad14" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card title="水费账单明细" style={{ marginTop: 24 }}>
        <Table
          columns={billColumns}
          dataSource={waterBills}
          rowKey="plot_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}

export default Stats;
