import React, { useState, useEffect } from "react";
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  InputNumber,
  DatePicker,
  message,
} from "antd";
import { PlusOutlined, CloudOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import api from "../api";
import { useAuth } from "../context/AuthContext";

function Weather() {
  const [weatherData, setWeatherData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const { hasRole } = useAuth();

  useEffect(() => {
    fetchWeatherData();
  }, []);

  const fetchWeatherData = async () => {
    setLoading(true);
    try {
      const response = await api.get("/api/weather", { params: { limit: 60 } });
      setWeatherData(response.data);
    } catch (error) {
      message.error("获取气象数据失败");
    }
    setLoading(false);
  };

  const handleAdd = () => {
    form.resetFields();
    setModalVisible(true);
  };

  const handleSubmit = async (values) => {
    try {
      const data = {
        date: values.date.format("YYYY-MM-DD"),
        temperature_avg: values.temperature_avg,
        temperature_max: values.temperature_max,
        temperature_min: values.temperature_min,
        rainfall: values.rainfall || 0,
        wind_speed: values.wind_speed || 0,
        sunshine_hours: values.sunshine_hours || 0,
        relative_humidity: values.relative_humidity || 0,
        region: values.region || "东区",
      };
      await api.post("/api/weather", data);
      message.success("添加成功");
      setModalVisible(false);
      fetchWeatherData();
    } catch (error) {
      message.error(error.response?.data?.detail || "添加失败");
    }
  };

  const columns = [
    {
      title: "日期",
      dataIndex: "date",
      key: "date",
      sorter: (a, b) => new Date(a.date) - new Date(b.date),
      defaultSortOrder: "descend",
    },
    {
      title: "平均气温(℃)",
      dataIndex: "temperature_avg",
      key: "temperature_avg",
    },
    {
      title: "最高气温(℃)",
      dataIndex: "temperature_max",
      key: "temperature_max",
    },
    {
      title: "最低气温(℃)",
      dataIndex: "temperature_min",
      key: "temperature_min",
    },
    {
      title: "降雨量(mm)",
      dataIndex: "rainfall",
      key: "rainfall",
      render: (v) => v?.toFixed(1),
    },
    {
      title: "风速(m/s)",
      dataIndex: "wind_speed",
      key: "wind_speed",
      render: (v) => v?.toFixed(1),
    },
    {
      title: "日照时数(h)",
      dataIndex: "sunshine_hours",
      key: "sunshine_hours",
      render: (v) => v?.toFixed(1),
    },
    {
      title: "相对湿度(%)",
      dataIndex: "relative_humidity",
      key: "relative_humidity",
      render: (v) => v?.toFixed(1),
    },
    {
      title: "区域",
      dataIndex: "region",
      key: "region",
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div
        style={{
          marginBottom: 16,
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <h2 style={{ margin: 0 }}>气象数据管理</h2>
        {hasRole(["admin", "manager"]) && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            录入气象数据
          </Button>
        )}
      </div>

      <Table
        columns={columns}
        dataSource={weatherData}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 15 }}
      />

      <Modal
        title="录入气象数据"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="date"
            label="日期"
            rules={[{ required: true, message: "请选择日期" }]}
          >
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <div
            style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}
          >
            <Form.Item
              name="temperature_avg"
              label="平均气温(℃)"
              rules={[{ required: true, message: "请输入平均气温" }]}
            >
              <InputNumber step={0.1} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item
              name="temperature_max"
              label="最高气温(℃)"
              rules={[{ required: true, message: "请输入最高气温" }]}
            >
              <InputNumber step={0.1} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item
              name="temperature_min"
              label="最低气温(℃)"
              rules={[{ required: true, message: "请输入最低气温" }]}
            >
              <InputNumber step={0.1} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item name="rainfall" label="降雨量(mm)" initialValue={0}>
              <InputNumber min={0} step={0.1} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item name="wind_speed" label="风速(m/s)" initialValue={0}>
              <InputNumber min={0} step={0.1} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item
              name="sunshine_hours"
              label="日照时数(h)"
              initialValue={0}
            >
              <InputNumber min={0} step={0.1} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item
              name="relative_humidity"
              label="相对湿度(%)"
              initialValue={60}
            >
              <InputNumber min={0} max={100} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item name="region" label="区域" initialValue="东区">
              <Input placeholder="请输入区域" />
            </Form.Item>
          </div>
          <Form.Item style={{ marginTop: 16 }}>
            <Button type="primary" htmlType="submit" block>
              提交
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default Weather;
