import React, { useState, useEffect } from "react";
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Tag,
} from "antd";
import { PlusOutlined, EyeOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
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

function Plots() {
  const [plots, setPlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const { hasRole } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlots();
  }, []);

  const fetchPlots = async () => {
    setLoading(true);
    try {
      const response = await api.get("/api/plots");
      setPlots(response.data);
    } catch (error) {
      message.error("获取地块列表失败");
    }
    setLoading(false);
  };

  const handleAdd = () => {
    form.resetFields();
    setModalVisible(true);
  };

  const handleSubmit = async (values) => {
    try {
      await api.post("/api/plots", values);
      message.success("创建成功");
      setModalVisible(false);
      fetchPlots();
    } catch (error) {
      message.error(error.response?.data?.detail || "创建失败");
    }
  };

  const columns = [
    {
      title: "地块编号",
      dataIndex: "plot_code",
      key: "plot_code",
    },
    {
      title: "面积(亩)",
      dataIndex: "area_mu",
      key: "area_mu",
    },
    {
      title: "作物类型",
      dataIndex: "crop_type",
      key: "crop_type",
      render: (v) => cropNames[v] || v,
    },
    {
      title: "土壤类型",
      dataIndex: "soil_type",
      key: "soil_type",
      render: (v) => soilNames[v] || v,
    },
    {
      title: "灌溉方式",
      dataIndex: "irrigation_method",
      key: "irrigation_method",
      render: (v) => irrigationNames[v] || v,
    },
    {
      title: "水源",
      dataIndex: "water_source",
      key: "water_source",
      render: (v) => waterSourceNames[v] || v,
    },
    {
      title: "生长阶段",
      dataIndex: "growth_stage",
      key: "growth_stage",
      render: (v) => <Tag color="blue">{growthStageNames[v] || v}</Tag>,
    },
    {
      title: "区域",
      dataIndex: "region",
      key: "region",
    },
    {
      title: "年度配额(m³)",
      dataIndex: "annual_quota",
      key: "annual_quota",
      render: (v) => v?.toFixed(2),
    },
    {
      title: "操作",
      key: "action",
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/plots/${record.id}`)}
          >
            详情
          </Button>
        </Space>
      ),
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
        <h2 style={{ margin: 0 }}>地块管理</h2>
        {hasRole(["admin", "manager"]) && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增地块
          </Button>
        )}
      </div>

      <Table
        columns={columns}
        dataSource={plots}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title="新增地块"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="plot_code"
            label="地块编号"
            rules={[{ required: true, message: "请输入地块编号" }]}
          >
            <Input placeholder="例如: P001" />
          </Form.Item>
          <Form.Item
            name="area_mu"
            label="面积(亩)"
            rules={[{ required: true, message: "请输入面积" }]}
          >
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item
            name="crop_type"
            label="作物类型"
            rules={[{ required: true, message: "请选择作物类型" }]}
          >
            <Select>
              <Select.Option value="rice">水稻</Select.Option>
              <Select.Option value="wheat">小麦</Select.Option>
              <Select.Option value="corn">玉米</Select.Option>
              <Select.Option value="cotton">棉花</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="soil_type"
            label="土壤类型"
            rules={[{ required: true, message: "请选择土壤类型" }]}
          >
            <Select>
              <Select.Option value="sandy">砂土</Select.Option>
              <Select.Option value="loam">壤土</Select.Option>
              <Select.Option value="clay">粘土</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="irrigation_method"
            label="灌溉方式"
            rules={[{ required: true, message: "请选择灌溉方式" }]}
          >
            <Select>
              <Select.Option value="flood">漫灌</Select.Option>
              <Select.Option value="sprinkler">喷灌</Select.Option>
              <Select.Option value="drip">滴灌</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="water_source"
            label="水源"
            rules={[{ required: true, message: "请选择水源" }]}
          >
            <Select>
              <Select.Option value="reservoir">水库</Select.Option>
              <Select.Option value="river">河流</Select.Option>
              <Select.Option value="groundwater">地下水</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="region" label="区域">
            <Input placeholder="例如: 东区" />
          </Form.Item>
          <Form.Item
            name="growth_stage"
            label="生长阶段"
            initialValue="initial"
          >
            <Select>
              <Select.Option value="initial">初期</Select.Option>
              <Select.Option value="development">发育期</Select.Option>
              <Select.Option value="mid">中期</Select.Option>
              <Select.Option value="late">末期</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="annual_quota" label="年度配额(m³)">
            <InputNumber
              min={0}
              style={{ width: "100%" }}
              placeholder="留空则按面积自动计算"
            />
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

export default Plots;
