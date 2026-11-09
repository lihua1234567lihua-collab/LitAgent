# 启动 LitAgent 前端

LitAgent 前端由 FastAPI 提供服务，页面文件位于项目根目录的 `static/index.html`。无需单独启动前端开发服务器。

## 启动

在项目根目录 `D:\Agent_Project\mini-agent` 打开终端，先确认根目录 `.env` 中配置了 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=你的_API_Key
```

然后运行：

```bash
uv run uvicorn api.main:app --reload
```

启动成功后，在浏览器打开：

```text
http://127.0.0.1:8000/
```

API 文档地址：`http://127.0.0.1:8000/docs`。

按 `Ctrl+C` 停止服务。

> 请从项目根目录运行命令。FastAPI 启动时会初始化 Agent Graph 和 SQLite checkpoint 连接，并在服务关闭时释放连接。
