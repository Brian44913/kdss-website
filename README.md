# KDSS - 分布式存储系统

KDSS（Distributed Storage System）是一套高性能、高可靠的分布式存储系统，基于纠删码（Erasure Coding）提供数据冗余保护，采用裸盘直写引擎实现极致 I/O 性能。系统提供 POSIX 文件系统挂载（FUSE）和 S3 兼容接口两种访问方式，内置 Web 管理控制台，支持自动故障修复与数据均衡。

## 特性

- **纠删码冗余** — 基于 Reed-Solomon 算法，支持 EC(5,2) / EC(9,2) / EC(18,3) / EC(29,3) 四种配置，根据集群规模自动选择最优策略
- **裸盘直写引擎** — 绕过操作系统文件系统，直接操作块设备，消除文件系统元数据开销，最大化磁盘吞吐。顺序追加写入模式大幅降低磁盘随机 I/O，减少磁头寻道磨损，配合智能写入合并与可调 fsync 策略，**显著延长 HDD 使用寿命、降低故障率，从而减少数据重建频次和硬件更换成本**
- **S3 兼容网关** — 支持 PutObject、GetObject、Multipart Upload 等核心 S3 API，可直接对接现有 S3 客户端和工具链
- **FUSE 文件系统** — POSIX 语义挂载，应用程序无感知访问分布式存储，支持读写缓冲、并发调优和读写限速
- **StatFS / Fsync** — FUSE 客户端支持 `df -h` 显示集群真实容量，Fsync 确保数据持久化
- **Web 管理控制台** — Vue 3 + Element Plus 构建，提供集群监控、Bucket 管理、访问密钥管理等可视化操作界面
- **自动故障修复** — 自动检测降级条带并触发 Reed-Solomon 重建，按冗余损失优先级排序，支持超时自动重试
- **数据均衡** — 监控磁盘利用率分布，自动迁移数据分片到最低使用率磁盘，保持集群负载均衡
- **垃圾回收** — 支持回收站机制的两阶段 GC，防止误删数据；GC 删除支持手动 CLI 触发和自动超时回收（`auto_gc_pending_hours`，默认 48h），支持从已清除的回收站中批量恢复文件；自动清理超时 Multipart Upload
- **在线巡检** — 后台 CRC32 校验扫描，持续验证数据完整性
- **熔断与重试** — 客户端内置 per-node 熔断器（CLOSED/OPEN/HALF_OPEN），指数退避重试，写仲裁保护
- **磁盘自动隔离** — 基于滑动窗口 I/O 错误计数，自动隔离故障磁盘，心跳上报 SMART 健康数据
- **优雅关机** — Master/Storage 支持 30 秒优雅停机超时，确保在途请求处理完成
- **Prometheus 监控** — 全量指标输出（`kdss_*` 命名空间），内置告警规则模板，可直接对接 Grafana 面板，内置 pprof 调试端点
- **无缝滚动升级** — 利用 EC 容错能力，逐节点升级期间服务持续可用

## 架构

```
                        ┌─────────────────────────────────┐
                        │         客户端 / 应用            │
                        └──────┬──────────────┬───────────┘
                               │              │
                    FUSE 挂载  │              │  S3 API
                               │              │
                ┌──────────────▼──┐    ┌──────▼──────────┐
                │   ksfs (FUSE)   │    │  S3 Gateway     │
                └──────────┬──────┘    └──────┬──────────┘
                           │    gRPC          │
                    ┌──────▼──────────────────▼──────┐
                    │                                │
     ┌──────────────▼──────────────┐     ┌──────────▼────────┐
     │  混合节点 ×3~7（默认部署）    │◄───►│   MongoDB 副本集   │
     │  Master + Storage 同机运行   │     │   (元数据存储)      │
     │  ├ Master gRPC :6700        │     └───────────────────┘
     │  ├ Storage gRPC :6800       │
     │  ├ S3 :9000 / Web :8081     │
     │  └ 裸盘 ×N                  │
     └──────────────┬──────────────┘
                    │ gRPC
        ┌───────────┼───────────────┐
        │           │               │
   ┌────▼───┐  ┌───▼────┐   ┌─────▼───┐
   │Storage  │  │Storage │   │Storage  │
   │  Node   │  │ Node   │   │  Node   │    × N（其余服务器）
   │ ┌────┐  │  │┌────┐  │   │ ┌────┐  │
   │ │裸盘│  │  ││裸盘│  │   │ │裸盘│  │
   │ │×N  │  │  ││×N  │  │   │ │×N  │  │
   │ └────┘  │  │└────┘  │   │ └────┘  │
   └─────────┘  └────────┘   └─────────┘
```

**默认部署模式：混合部署** — 2~3 台服务器同时运行 Master + Storage 两个进程，其余服务器只运行 Storage。所有服务器的 HDD 均参与数据存储，无资源浪费。

### 核心组件

| 组件 | 说明 | 默认端口 |
|------|------|----------|
| **Master** | 元数据管理、Leader 选举、条带分配、自动修复/均衡/GC 调度 | gRPC `:6700`，Metrics `:6701`，Web `:8081`，S3 `:9000` |
| **Storage** | 裸盘存储引擎、分片读写、CRC32 校验、后台巡检与压缩 | gRPC `:6800`，Metrics `:6801` |
| **ksfs** | FUSE 客户端、EC 编解码、文件系统语义适配 | — |
| **Web Console** | 集群监控、Bucket/密钥管理、运维操作界面 | `:8081`（内嵌于 Master） |

## 纠删码策略

系统根据存储节点数量自动选择最优 EC 配置：

| EC 配置 | 数据分片 | 校验分片 | 总分片 | 最低/建议节点数 | 容忍故障数 | 得盘率 | 集群原始容量† | 可写总容量† |
|---------|---------|---------|-------|---------------|-----------|--------|-------------|-----------|
| EC(5,2) | 5 | 2 | 7 | 8 / 9 | 2 | 71.4% | 4,716 TB | 3,369 TB |
| EC(9,2) | 9 | 2 | 11 | 12 / 13 | 2 | 81.8% | 6,812 TB | 5,575 TB |
| EC(18,3) | 18 | 3 | 21 | 22 / 24 | 3 | 85.7% | 12,576 TB | 10,779 TB |
| EC(29,3) | 29 | 3 | 32 | 33 / 36 | 3 | 90.6% | 18,864 TB | 17,096 TB |
| EC(31,2)⚠ | 31 | 2 | 33 | 34 / 36 | 2 | 93.9% | 18,864 TB | 17,721 TB |

> † 容量示例按**建议节点数**、每节点 **36 × 16TB HDD**（标称 16TB，实际 16,000,900,661,248 字节 ≈ 14.55 TB，单节点 524 TB）计算。
> - **得盘率** = 数据分片 ÷ 总分片，表示原始容量中可存储用户数据的比例。
> - **可写总容量** = 集群原始容量 × 得盘率。
> - 以 EC(29,3) 为例：36 节点 × 524 TB = 18,864 TB 原始容量，可写 18,864 × 29/32 ≈ **17,096 TB（16.7 PiB）**。
>
> ⚠ **EC(31,2) 模式仅适用于全新的存储服务器和全新企业级硬盘，且必须在 Tier 3+ 标准的 IDC 机房，配备 24 小时人员值守随时处理硬件故障。** 该模式仅容忍 2 个同时故障，容错能力低于 EC(29,3)，以换取更高的得盘率。

## 快速开始

### 前置要求

- Go 1.24+
- Protocol Buffers 编译器 (`protoc`)
- MongoDB 8.0+（副本集模式）
- FUSE 3（客户端节点）
- Node.js 18+（构建 Web 控制台）
- Ubuntu 24.04 LTS（推荐）

### 编译

```bash
git clone https://github.com/Brian44913/kdss.git
cd kdss

# 完整构建（proto + web + 后端）
make all

# 仅构建后端
make build

# 构建 FUSE 客户端
make build-ksfs
```

编译产物：
- `bin/kdss` — 主程序（Master / Storage / Admin CLI）
- `bin/ksfs` — FUSE 挂载客户端

### 格式化磁盘

将裸盘设备格式化为 KDSS 存储格式（写入 SuperBlock）：

```bash
sudo kdss format --device /dev/sda
sudo kdss format --device /dev/sdb
# ... 对每个存储磁盘重复
```

### 启动 Master 节点

```bash
# 编辑配置
sudo cp configs/master.toml.example /etc/kdss/master.toml
sudo vim /etc/kdss/master.toml

# 启动服务
sudo systemctl start kdss-master
sudo systemctl enable kdss-master
```

核心配置项（`master.toml`）：

```toml
listen = ":6700"
mongo_uri = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=kdss"
mongo_db = "kdss"
web_listen = ":8081"
s3_listen = ":9000"
jwt_secret = ""       # JWT 签名密钥（必填，至少 32 字符）
encrypt_key = ""      # AES-256-GCM 加密密钥（必填，留空将拒绝启动）

[ec]
data_shards = 29
parity_shards = 3

[leader]
lock_ttl_sec = 15
renew_interval_sec = 5

[gc]
interval_sec = 3600              # housekeeping 巡检间隔（stale stripes / multipart 清理）
compact_threshold = 0.2
auto_gc_pending_hours = 48       # gc_pending 超过此时间自动删除 shard（0=禁用）

[log]
level = "info"
file = "/var/log/kdss/master.log"
```

### 启动 Storage 节点

```bash
sudo cp configs/storage.toml.example /etc/kdss/storage.toml
sudo vim /etc/kdss/storage.toml

sudo systemctl start kdss-storage
sudo systemctl enable kdss-storage
```

核心配置项（`storage.toml`）：

```toml
node_id = "storage-01"
listen = ":6800"
master_addrs = ["10.0.0.1:6700", "10.0.0.2:6700", "10.0.0.3:6700"]
index_dir = "/opt/kdss/index"

[[disks]]
disk_id = 0
device = "/dev/sda"

[[disks]]
disk_id = 1
device = "/dev/sdb"

[heartbeat]
interval_sec = 60
timeout_sec = 180

[compactor]
enabled = true
threshold = 0.2

[log]
level = "info"
file = "/var/log/kdss/storage.log"
```

### 挂载文件系统

```bash
# 使用 ksfs 客户端挂载
sudo cp configs/mount.toml.example /etc/ksfs/mount.toml
sudo vim /etc/ksfs/mount.toml

sudo ksfs -c /etc/ksfs/mount.toml
```

挂载配置（`mount.toml`）：

```toml
[cluster]
masters = ["10.0.0.1:6700", "10.0.0.2:6700", "10.0.0.3:6700"]

[auth]
access_key = "your-access-key"
secret_key = "your-secret-key"
bucket = "my-bucket"

[mount]
mountpoint = "/mnt/kdss"

[performance]
write_buffer_mb = 64
read_ahead_mb = 16
max_concurrent_reads = 32
max_concurrent_writes = 16
```

挂载后即可像本地目录一样读写：

```bash
cp /path/to/file /mnt/kdss/
ls -la /mnt/kdss/
```

## S3 接口

系统内置 S3 兼容网关（默认端口 `:9000`），支持以下操作：

| 操作 | API |
|------|-----|
| 列出 Bucket | `GET /` |
| 创建 Bucket | `PUT /{bucket}` |
| 删除 Bucket | `DELETE /{bucket}` |
| 列出对象 (V2) | `GET /{bucket}?list-type=2` |
| 上传对象 | `PUT /{bucket}/{key}` |
| 下载对象 | `GET /{bucket}/{key}`（支持 Range GET） |
| 复制对象 | `PUT /{bucket}/{key}` + `X-Amz-Copy-Source` |
| 删除对象 | `DELETE /{bucket}/{key}` |
| 查询对象信息 | `HEAD /{bucket}/{key}` |
| 查询 Bucket | `HEAD /{bucket}` |
| 分片上传 | `POST /{bucket}/{key}?uploads` |
| 上传分片 | `PUT /{bucket}/{key}?partNumber=N&uploadId=ID` |
| 完成分片上传 | `POST /{bucket}/{key}?uploadId=ID` |
| 列出分片上传 | `GET /{bucket}?uploads` |
| 取消分片上传 | `DELETE /{bucket}/{key}?uploadId=ID` |
| 批量删除对象 | `POST /{bucket}?delete` |
| Presigned URL | 支持 AWS Signature V4 Query String 认证 |

使用 AWS CLI 示例：

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key

aws s3 --endpoint-url http://10.0.0.1:9000 ls
aws s3 --endpoint-url http://10.0.0.1:9000 cp file.tar s3://my-bucket/
aws s3 --endpoint-url http://10.0.0.1:9000 ls s3://my-bucket/
```

## 集群管理

### 管理命令

`kdss admin` 提供完整的集群运维命令集：

```bash
# 连接指定 Master
kdss admin --master 10.0.0.1:6700

# 集群概览
kdss admin cluster status

# 节点管理
kdss admin node list
kdss admin node info --node <node-id>
kdss admin node drain --node <node-id>          # 安全下线（迁移数据后移除）
kdss admin node undrain --node <node-id>        # 取消 drain
kdss admin node offline --node <node-id>        # 标记离线
kdss admin node online --node <node-id>         # 标记上线
kdss admin node remove --node <node-id>

# 磁盘管理
kdss admin disk list [--node <node-id>]
kdss admin disk info --node <node-id> --disk-id <id>
kdss admin disk add --node <addr>:6800 --device <device>
kdss admin disk remove --node <node-id> --disk-id <id>
kdss admin disk replace --node <node-id> --disk-id <id>
kdss admin disk set-state --node <node-id> --disk-id <id> --state <online|offline>

# 数据修复
kdss admin repair status
kdss admin repair disk --node <node-id> --disk-id <id>
kdss admin repair node --node <node-id>
kdss admin repair stripe --stripe-id <id>

# 数据均衡
kdss admin balance start [--threshold 10.0]
kdss admin balance status
kdss admin balance stop

# 磁盘压缩（回收 GC 后的物理空间）
kdss admin compact start                           # 全集群压缩
kdss admin compact start --node <id>               # 指定节点
kdss admin compact start --node <id> --disk-id <n> # 指定磁盘

# 垃圾回收
kdss admin gc status
kdss admin gc start                                      # 手动触发一次 GC 删除
kdss admin gc purge-recycle [--bucket <name>] [--force]  # 清除回收站

# 数据恢复（从已清除的回收站恢复）
kdss admin gc recover-list --bucket <name>                              # 列出可恢复文件
kdss admin gc recover --bucket <name> --target-dir <path> [--force]    # 批量恢复到指定目录

# 数据巡检
kdss admin check start [--type full|meta|data|overlap]
kdss admin check status
kdss admin check stop

# 故障检测
kdss admin fault status
kdss admin fault check-disk <node-id> <disk-id>
kdss admin fault scan

# Bucket 用量管理
kdss admin bucket reconcile --bucket <name> --dry-run   # 查看用量差异
kdss admin bucket reconcile --bucket <name>              # 实际校正用量

# 许可证管理
kdss admin license status                # 查看许可证状态
kdss admin license upload <file>         # 上传新许可证

# 磁盘身份扫描（离线，无需 Master 连接）
kdss scan /dev/sd[b-z]                   # 查看所有磁盘的 UUID/NodeID/DiskID
kdss scan --toml /dev/sd[b-z]            # 输出 storage.toml 格式
```

### Web 控制台

访问 `http://<master-ip>:8081` 打开 Web 管理控制台，提供：

- 集群仪表盘（节点/磁盘/容量总览）
- Master 节点状态（Leader/Follower、版本、运行时间）
- 节点管理（节点列表/详情/磁盘 UUID）
- Bucket 管理（创建/删除/域名绑定/配额/ACL）
- 访问密钥管理
- 对象浏览器（上传/下载/批量删除）
- 监控面板（Prometheus 指标可视化）
- 告警设置与告警历史
- 操作日志
- 回收站管理
- 用户管理（RBAC 角色分配）
- 许可证管理
- 系统设置

## 项目结构

```
kdss/
├── cmd/
│   ├── kdss/main.go              # 主程序入口（master/storage/mount/format/scan/admin/bench）
│   └── ksfs/main.go              # FUSE 客户端入口
├── configs/
│   ├── master.toml.example       # Master 配置模板
│   ├── storage.toml.example      # Storage 配置模板
│   ├── mount.toml.example        # FUSE 挂载配置模板
│   ├── kdss-master.service       # Master systemd 服务
│   ├── kdss-storage.service      # Storage systemd 服务
│   ├── ksfs.service              # FUSE 客户端 systemd 服务
│   ├── kdss-license-server.service # License Server systemd 服务
│   ├── prometheus-alerts.yml     # Prometheus 告警规则模板
│   ├── logrotate-kdss            # 日志轮转配置
│   └── nginx.conf.example        # Nginx 反向代理示例
├── deploy/
│   ├── gen-configs.sh            # 批量生成集群配置
│   └── fix-disk-configs.sh       # 修复磁盘配置
├── docs/
│   ├── cli.md                    # CLI 命令参考手册
│   ├── deployment.md             # 部署指南
│   ├── capacity-planning.md      # 容量规划指南
│   ├── fault-recovery.md         # 故障恢复手册
│   ├── maintenance.md            # 日常维护手册
│   ├── troubleshooting.md        # 故障排查手册
│   ├── upgrade.md                # 无缝升级指南
│   └── ksfs.md                   # FUSE 客户端文档
├── internal/
│   ├── admin/                    # Admin CLI 命令实现
│   ├── alert/                    # 告警通知
│   ├── auth/                     # 认证与 JWT
│   ├── config/                   # TOML 配置解析
│   ├── ec/                       # 纠删码（Reed-Solomon）
│   ├── fuse/                     # FUSE 文件系统实现
│   ├── hashring/                 # 一致性哈希
│   ├── master/                   # Master 节点核心逻辑
│   ├── metrics/                  # Prometheus 指标
│   ├── proto/                    # Protocol Buffers 定义
│   ├── s3/                       # S3 兼容网关
│   ├── storage/                  # 裸盘存储引擎
│   ├── tlsutil/                  # gRPC mTLS 凭据管理
│   └── web/                      # Web 控制台后端
├── scripts/
│   ├── deploy.sh                 # 自动化部署脚本
│   ├── format-disks.sh           # 批量磁盘格式化
│   └── hardware-check.sh         # 集群物料批量检查
├── web/                          # Vue 3 前端源码
├── Makefile
└── go.mod
```

## 监控

系统通过 Prometheus 暴露全量指标，命名空间为 `kdss_*`。

### 关键指标

**集群级别**

| 指标 | 说明 |
|------|------|
| `kdss_cluster_nodes_total` | 集群节点总数 |
| `kdss_cluster_nodes_online` | 在线节点数 |
| `kdss_cluster_disks_total` | 磁盘总数 |
| `kdss_cluster_disks_online` | 在线磁盘数 |
| `kdss_cluster_capacity_bytes` | 集群总容量 |
| `kdss_cluster_used_bytes` | 已用容量 |
| `kdss_metadata_stripes_total` | 条带总数 |
| `kdss_metadata_inodes_total` | Inode 总数 |

**Master 服务**

| 指标 | 说明 |
|------|------|
| `kdss_master_grpc_requests_total` | gRPC 请求总数（按方法/状态码） |
| `kdss_master_grpc_request_duration_seconds` | gRPC 请求延迟（按方法） |
| `kdss_master_is_leader` | 当前是否为 Leader（1=是） |
| `kdss_repair_tasks_active` | 活跃修复任务数 |
| `kdss_repair_shards_repaired_total` | 已修复分片总数 |
| `kdss_balance_tasks_active` | 活跃均衡任务数 |
| `kdss_balance_migrated_bytes_total` | 均衡迁移字节数 |
| `kdss_gc_pending_stripes` | 待回收条带数 |
| `kdss_gc_deleted_stripes_total` | 已回收条带总数 |
| `kdss_gc_stale_uploads_cleaned_total` | 清理超时上传数 |
| `kdss_mongo_pool_checked_out_total` | MongoDB 连接池取出连接次数 |
| `kdss_mongo_pool_checked_in_total` | MongoDB 连接池归还连接次数 |
| `kdss_mongo_pool_created_total` | MongoDB 连接池创建连接次数 |
| `kdss_mongo_pool_closed_total` | MongoDB 连接池关闭连接次数 |
| `kdss_mongo_pool_in_use` | MongoDB 连接池当前使用中连接数 |

**Storage 节点**

| 指标 | 说明 |
|------|------|
| `kdss_storage_disk_write_bytes_total` | 磁盘写入字节数（按磁盘） |
| `kdss_storage_disk_read_bytes_total` | 磁盘读取字节数（按磁盘） |
| `kdss_storage_disk_io_errors_total` | 磁盘 I/O 错误数（按磁盘） |
| `kdss_storage_disks_isolated` | 当前自动隔离磁盘数 |
| `kdss_storage_shard_writes_total` | 分片写入次数 |
| `kdss_storage_shard_reads_total` | 分片读取次数 |
| `kdss_storage_checker_corrupt_shards_total` | 巡检发现损坏分片数 |
| `kdss_storage_compactor_reclaimed_bytes_total` | 压缩回收字节数 |

**S3 网关**

| 指标 | 说明 |
|------|------|
| `kdss_s3_requests_total` | S3 请求总数（按方法/操作/状态码） |
| `kdss_s3_request_duration_seconds` | S3 请求延迟（按操作） |
| `kdss_s3_upload_bytes_total` | S3 上传字节数 |
| `kdss_s3_download_bytes_total` | S3 下载字节数 |

**FUSE 客户端**

| 指标 | 说明 |
|------|------|
| `kdss_fuse_ops_total` | FUSE 操作总数（按操作类型） |
| `kdss_fuse_op_duration_seconds` | FUSE 操作延迟（按操作类型） |
| `kdss_fuse_read_bytes_total` | FUSE 读取字节数 |
| `kdss_fuse_write_bytes_total` | FUSE 写入字节数 |
| `kdss_fuse_circuit_breaker_open` | 节点熔断器状态（1=开启） |
| `kdss_fuse_conn_pool_active` | 连接池活跃连接数 |

### Prometheus 配置示例

```yaml
scrape_configs:
  - job_name: 'kdss-master'
    static_configs:
      - targets: ['10.0.0.1:6701', '10.0.0.2:6701', '10.0.0.3:6701']

  - job_name: 'kdss-storage'
    static_configs:
      - targets: ['10.0.1.1:6801', '10.0.1.2:6801', '10.0.1.3:6801']

rule_files:
  - 'prometheus-alerts.yml'   # 内置告警规则模板
```

项目提供了 `configs/prometheus-alerts.yml` 告警规则模板，覆盖节点离线/心跳、磁盘容量/错误/隔离、修复积压/停滞、GC 积压/回滚、均衡失败/积压、gRPC 延迟/错误率、S3 网关错误率、Leader 选举/可用性、MongoDB 健康、压缩超时、数据损坏、集群容量、许可证到期等 32 条告警规则。

## 技术栈

| 分类 | 技术 |
|------|------|
| 语言 | Go 1.24 |
| RPC 框架 | gRPC + Protocol Buffers |
| 元数据存储 | MongoDB（副本集） |
| 纠删码 | klauspost/reedsolomon |
| FUSE | hanwen/go-fuse/v2 |
| HTTP 框架 | Gin |
| CLI 框架 | Cobra |
| 认证 | JWT (golang-jwt/jwt/v5) |
| 本地索引 | BadgerDB |
| 日志 | Zap |
| 配置 | TOML |
| 监控 | Prometheus client_golang |
| 前端 | Vue 3 + Element Plus + Vite |

## Makefile 目标

```bash
make all              # 完整构建：proto → web → 后端 → ksfs
make build            # 编译主程序 → bin/kdss
make build-ksfs       # 编译 FUSE 客户端 → bin/ksfs
make proto            # 从 .proto 生成 Go 代码
make build-web        # 构建 Web 前端
make embed-web        # 构建 Web 前端并嵌入到 Go 二进制
make test             # 运行全部测试
make install          # 安装 bin/kdss → /usr/local/bin/kdss
make install-master   # 安装 + 配置 Master systemd 服务
make install-storage  # 安装 + 配置 Storage systemd 服务
make install-ksfs     # 安装 + 配置 FUSE 客户端 systemd 服务
make clean            # 清理构建产物
make tidy             # go mod tidy
```

## 文档

| 文档 | 说明 |
|------|------|
| CLI 命令参考 | kdss / ksfs 全部命令、参数、用法示例与运维场景速查 |
| 部署指南 | 集群规划、环境准备、Master/Storage/FUSE 部署、MongoDB 副本集配置 |
| 容量规划 | 内存、SSD、MongoDB、CPU 资源评估方法与 Filecoin 场景实例 |
| 日常维护 | 健康检查、磁盘管理、巡检/GC/压缩、监控告警、日志管理 |
| 故障排查 | 12 类故障场景的症状分析、诊断方法与恢复步骤 |
| 无缝升级 | 滚动升级流程、回滚方案、版本兼容性说明 |
| FUSE 客户端 | ksfs 安装、配置、挂载参数与性能调优 |

> 完整文档随产品交付，或联系我们获取。

## 许可证

版权所有，保留所有权利。
