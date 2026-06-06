import React, { useState } from "react";
import { Form, Input, Button, message, Card } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Login() {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    const result = await login(values.username, values.password);
    setLoading(false);
    if (result.success) {
      message.success("登录成功");
      navigate("/dashboard");
    } else {
      message.error(result.message);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">🌾 农田灌溉智能决策系统</h1>
        <Form name="login" onFinish={onFinish} autoComplete="off" size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: "请输入用户名" }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: "请输入密码" }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              登 录
            </Button>
          </Form.Item>
        </Form>
        <div
          style={{
            marginTop: 24,
            fontSize: 12,
            color: "#999",
            textAlign: "center",
          }}
        >
          <p>管理员: admin / admin123</p>
          <p>灌区管理员: manager1 / mgr123 | manager2 / mgr123</p>
          <p>农户: farmer1 / farm123 | farmer2 / farm123 | farmer3 / farm123</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
