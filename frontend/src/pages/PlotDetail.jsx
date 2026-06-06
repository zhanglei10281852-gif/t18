import React, { useState, useEffect } from "react";
import {
  Card,
  Descriptions,
  Table,
  Spin,
  Button,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  DatePicker,
  message,
  Tag,
} from "antd";
import { ArrowLeftOutlined, PlusOutlined } from "@ant-design/icons";
import { useParams, useNavigate } from "react-router-dom";
import dayjs from "dayjs";
import {
  ComposedChart,
  Line,
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

const soilNames = {
  sandy: "砂土",
  loam: "壤土",
  clay: "粘土",
};

const irrigationNames = {
  flood: "漫灌",
  sprinkler: "喷灌",
  drip: "滴灌",
};

const waterSourceNames = {
  reservoir: "水库",
  river: "河流",
  groundwater: "地下水",
};

const growthStageNames = {
  initial: "初期",
  development: "发育期",
  mid: "中期",
  late: "末期",
};

function PlotDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [plot, setPlot] = useState(null);
  const [records, setRecords] = useState([]);
  const [balanceData, setBalanceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const { hasRole } = useAuth();

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [plotRes, recordsRes, weatherRes] = await Promise.all([
        api.get(`/api/plots/${id}`),
        api.get("/api/irrigation/records", {
          params: { plot_id: id, limit: 50 },
        }),
        api.get("/api/weather", { params: { limit: 30 } }),
      ]);
      setPlot(plotRes.data);
      setRecords(recordsRes.data);

      const sortedWeather = [...weatherRes.data].sort(
        (a, b) => new Date(a.date) - new Date(b.date),
      );
      const balance = sortedWeather.map((w) => {
        const dayRecords = recordsRes.data.filter(
          (r) => dayjs(r.irrigation_date).format("YYYY-MM-DD") === w.date,
        );
        const irrigationTotal = dayRecords.reduce(
          (sum, r) => sum + r.water_amount_m3,
          0,
        );
        const etc = w.temperature_avg * 0.3;
        return {
          date: w.date,
          et: +etc.toFixed(2),
          rainfall: +w.rainfall.toFixed(2),
          irrigation: +irrigationTotal.toFixed(2),
          balance: +(w.rainfall * 0.7 + irrigationTotal - etc).toFixed(2),
        };
      });
      setBalanceData(balance);
    } catch (error) {
      message.error("获取数据失败");
    }
    setLoading(false);
  };

  const handleAddRecord = () => {
    form.resetFields();
    setModalVisible(true);
  };

  const handleSubmitRecord = async (values) => {
    try {
      await api.post("/api/irrigation/records", {
        plot_id: parseInt(id),
        irrigation_date: values.irrigation_date.format("YYYY-MM-DD"),
        water_amount_m3: values.water_amount_m3,
        duration_hours: values.duration_hours || 0,
        irrigation_method: plot.irrigation_method,
        operator: "手动录入",
        notes: values.notes || "",
      });
      message.success("记录添加成功");
      setModalVisible(false);
      fetchData();
    } catch (error) {
      message.error("添加失败");
    }
  };

  const recordColumns = [
    {
      title: "灌溉日期",
      dataIndex: "irrigation_date",
      key: "irrigation_date",
    },
    {
      title: "用水量(m³)",
      dataIndex: "water_amount_m3",
      key: "water_amount_m3",
      render: (v) => v?.toFixed(2),
    },
    {
      title: "灌溉时长(小时)",
      dataIndex: "duration_hours",
      key: "duration_hours",
      render: (v) => v?.toFixed(1),
    },
    {
      title: "灌溉方式",
      dataIndex: "irrigation_method",
      key: "irrigation_method",
      render: (v) => irrigationNames[v] || v,
    },
    {
      title: "操作人",
      dataIndex: "operator",
      key: "operator",
    },
    {
      title: "备注",
      dataIndex: "notes",
      key: "notes",
    },
  ];

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/plots")}>
          返回
        </Button>
        <h2 style={{ margin: 0 }}>地块详情 - {plot?.plot_code}</h2>
      </Space>

      <Card title="基本信息" style={{ marginBottom: 24 }}>
        <Descriptions column={3}>
          <Descriptions.Item label="地块编号">
            {plot?.plot_code}
          </Descriptions.Item>
          <Descriptions.Item label="面积(亩)">
            {plot?.area_mu}
          </Descriptions.Item>
          <Descriptions.Item label="作物类型">
            {cropNames[plot?.crop_type] || plot?.crop_type}
          </Descriptions.Item>
          <Descriptions.Item label="土壤类型">
            {soilNames[plot?.soil_type] || plot?.soil_type}
          </Descriptions.Item>
          <Descriptions.Item label="灌溉方式">
            {irrigationNames[plot?.irrigation_method] ||
              plot?.irrigation_method}
          </Descriptions.Item>
          <Descriptions.Item label="水源">
            {waterSourceNames[plot?.water_source] || plot?.water_source}
          </Descriptions.Item>
          <Descriptions.Item label="生长阶段">
            <Tag color="blue">
              {growthStageNames[plot?.growth_stage] || plot?.growth_stage}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="区域">
            {plot?.region || "-"}
          </Descriptions.Item>
          <Descriptions.Item label="年度配额(m³)">
            {plot?.annual_quota?.toFixed(2)}
          </Descriptions.Item>
          <Descriptions.Item label="归属农户">
            {plot?.farmer?.real_name || plot?.farmer?.username || "-"}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="近30天土壤水分平衡" style={{ marginBottom: 24 }}>
        <div style={{ height: 350 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={balanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="rainfall" name="降雨补给(mm)" fill="#1890ff" />
              <Bar dataKey="irrigation" name="灌溉补给(m³)" fill="#52c41a" />
              <Line
                type="monotone"
                dataKey="et"
                name="ET蒸散(mm)"
                stroke="#ff4d4f"
                strokeWidth={2}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card
        title="灌溉历史记录"
        extra={
          hasRole(["admin", "manager"]) && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddRecord}
            >
              录入灌溉记录
            </Button>
          )
        }
      >
        <Table
          columns={recordColumns}
          dataSource={records}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="录入灌溉记录"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmitRecord}>
          <Form.Item
            name="irrigation_date"
            label="灌溉日期"
            rules={[{ required: true, message: "请选择日期" }]}
          >
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item
            name="water_amount_m3"
            label="用水量(m³)"
            rules={[{ required: true, message: "请输入用水量" }]}
          >
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="duration_hours" label="灌溉时长(小时)">
            <InputNumber min={0} step={0.5} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <InputNumber />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              提交
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default PlotDetail;
