# EasyTrain Agent 前端

这是 EasyTrain Agent 的前端项目，一个用于管理和监控训练任务的 Web 界面。它提供了数据标注、项目配置和日志查看等工具。

## ✨ 主要功能

- **项目管理**: 初始化和管理不同的训练项目。
- **文件系统交互**: 在项目工作区内读取、写入和修改文件。
- **命令执行**: 运行 Shell 命令和 Python 脚本。
- **日志查看器**: 用于查看实时日志的专用界面。
- **数据标注**: 用于数据注释任务的 UI。
- **配置向导**: 用于设置项目的分步指南。

## 🛠️ 技术栈

- **框架**: [Next.js](https://nextjs.org/)
- **语言**: [TypeScript](https://www.typescriptlang.org/)
- **样式**: [Tailwind CSS](https://tailwindcss.com/)
- **UI 组件**: [Shadcn/ui](https://ui.shadcn.com/)
- **状态管理**: [Zustand](https://github.com/pmndrs/zustand)
- **表单**: [React Hook Form](https://react-hook-form.com/)

## 🚀 本地开发

### 环境要求

- [Node.js](https.nodejs.org/) (建议使用 20.x 或更高版本)
- [npm](https://www.npmjs.com/) 或其他包管理器

### 安装与开发

1.  **克隆仓库:**
    ```bash
    git clone <your-repository-url>
    cd EasyTrainAgent/frontend
    ```

2.  **安装依赖:**
    ```bash
    npm install
    ```

3.  **运行开发服务器:**
    ```bash
    npm run dev
    ```

在浏览器中打开 [http://localhost:3000](http://localhost:3000) 查看结果。

## 📂 项目结构

- `app/`: 包含核心应用逻辑、路由 (App Router) 和 API 端点。
- `components/`: 共享的 UI 组件，包括 `shadcn/ui` 组件。
- `stores/`: 用于全局状态管理的 Zustand store。
- `lib/`: 工具函数。
- `hooks/`: 自定义 React 钩子。
- `types/`: TypeScript 类型定义。

## ✅ 待办事项

- [ ] **用户认证**: 实现用户登录和注册系统。
- [ ] **增强的错误处理**: 改进整个应用的错误处理和用户反馈。
- [ ] **API 扩展**: 为高级项目管理和监控添加更多 API 端点。
- [ ] **测试**: 引入单元测试和集成测试 (例如，使用 Jest 和 React Testing Library)。
- [ ] **UI/UX 优化**: 优化数据标注和向导页面的 UI，以提高可用性。
- [ ] **国际化 (i18n)**: 添加对多种语言的支持。
- [ ] **文档**: 为组件和 API 添加更详细的文档。
