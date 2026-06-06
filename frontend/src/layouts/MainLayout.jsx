import React from "react";
import { Layout, Menu, Avatar, Dropdown, Button } from "antd";
import {
  DashboardOutlined,
  EnvironmentOutlined,
  CloudOutlined,
  BarChartOutlined,
  DatabaseOutlined,
  UserOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const { Header, Sider, Content } = Layout;

const roleNames = {
  admin: "管理员",
  manager: "灌区管理员",
  farmer: "农户",
};

function MainLayout() {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: "/dashboard",
      icon: <DashboardOutlined />,
      label: "仪表盘",
    },
    {
      key: "/plots",
      icon: <EnvironmentOutlined />,
      label: "地块管理",
    },
    {
      key: "/weather",
      icon: <CloudOutlined />,
      label: "气象数据",
    },
    {
      key: "/water-rights",
      icon: <DatabaseOutlined />,
      label: "水权管理",
    },
    {
      key: "/stats",
      icon: <BarChartOutlined />,
      label: "统计分析",
    },
  ];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const userMenu = {
    items: [
      {
        key: "role",
        label: `角色: ${roleNames[user?.role] || user?.role}`,
        disabled: true,
      },
      { type: "divider" },
      {
        key: "logout",
        icon: <LogoutOutlined />,
        label: "退出登录",
        onClick: handleLogout,
      },
    ],
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider width={220} theme="dark" className="sidebar">
        <div
          style={{
            height: 64,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontSize: 18,
            fontWeight: "bold",
            borderBottom: "1px solid #002140",
          }}
        >
          🌾 灌溉决策系统
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ marginTop: 16 }}
        />
      </Sider>
      <Layout>
        <Header className="layout-header" style={{ padding: "0 24px" }}>
          <div style={{ color: "white", fontSize: 16 }}>
            农田灌溉智能决策与用水量核算系统
          </div>
          <Dropdown menu={userMenu} placement="bottomRight">
            <div className="user-info" style={{ cursor: "pointer" }}>
              <Avatar size="small" icon={<UserOutlined />} />
              <span>{user?.real_name || user?.username}</span>
              <span style={{ fontSize: 12, color: "#aaa" }}>
                ({roleNames[user?.role]})
              </span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: 0, minHeight: 280, background: "#f0f2f5" }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

export default MainLayout;
