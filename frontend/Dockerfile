FROM docker.m.daocloud.io/node:20-alpine

WORKDIR /app

# 复制依赖文件
COPY package.json pnpm-lock.yaml ./

# 设置 npm 镜像并安装 pnpm
RUN npm config set registry https://registry.npmmirror.com && \
    npm install -g pnpm

# 设置 pnpm 镜像并安装依赖
RUN pnpm config set registry https://registry.npmmirror.com && \
    pnpm install --frozen-lockfile

# 复制源代码
COPY . .

EXPOSE 5173

# 运行开发服务器
CMD ["pnpm", "run", "dev", "--host"]