# 个人服务部署方案

## 1. 目录结构

- **oci-image**: 需要自行构建的镜像（caddy、excalidraw、seaweedfs 等）
- **k8s-yaml**: K8S / Podman Kube 配置文件
- **quadlet**: Quadlet 服务
- **cloud-init**: 云镜像自动部署配置

Forgejo、Vaultwarden、Drawio、PlantUML、Dufs、Nginx Proxy Manager 直接使用上游镜像，不再经过 `oci-image` 代理构建。

## 2. 默认端口占用

Forgejo、Vaultwarden、Drawio、PlantUML、Dufs 默认只监听容器网络，由反向代理（Caddy 或 Nginx Proxy Manager，二选一，占用 80/443/81）转发；其余服务按下列端口映射到宿主机。Quadlet 额外映射的端口单独标注。

- **反向代理**
  - 80/443: HTTP/HTTPS
  - 81: 管理后台（Nginx Proxy Manager；建议只监听 127.0.0.1）

- **Forgejo**
  - 2222: Git SSH（直接映射到宿主机）
  - 3000: 主站点（仅容器网络；Quadlet 映射 127.0.0.1:3000）

- **Vaultwarden**
  - 80: 主站点（仅容器网络；Quadlet 映射 127.0.0.1:3010）

- **Drawio**
  - 8080: 主站点（仅容器网络；Quadlet 映射 127.0.0.1:3020）

- **PlantUML**
  - 8080: 主站点（仅容器网络；Quadlet 映射 127.0.0.1:3040）

- **Dufs**
  - 5000: 文件服务（仅容器网络，由反向代理转发）

- **Excalidraw**
  - 3030: 主站点
  - 3031: 协同服务器

- **Blessing Skin**
  - 25580: 主站点（127.0.0.1）

- **Emotion Library**
  - 3050: 主站点

- **Seaweed S3**
  - 8333: S3 接口
  - 8888: Filer 面板
  - 9333: 状态面板

## 3. 服务拉起

### 3.1. Podman Kube（推荐）

**普通服务:**

```bash
podman kube play k8s.forgejo.yaml
```

**反向代理（Nginx Proxy Manager，占用 80/443/81）:**

```bash
podman kube play k8s.nginx-proxy-manager.yaml
```

**反向代理（Caddy，host 网络）:**

```bash
podman kube play --network host k8s.caddy.yaml
```

> NPM 与 Caddy 都会占用 80/443/81，同一台机器只能启用其中一个。
> 需要反代的服务不再发布宿主机端口，请在 NPM 中把 Forward Hostname 指向对应容器名或 Pod IP。

### 3.2. Quadlet

修改 `quadlet/` 下的文件后，需要重新生成并重启：

```bash
systemctl --user daemon-reload
systemctl --user restart forgejo-pod
```

## 4. Proxmox KVM 配置建议

- **OpenWrt**

```conf
agent: 1
balloon: 256
bios: ovmf
boot: order=scsi0;ide2;net0
cores: 1
cpu: host
efidisk0: local-lvm:base-200-disk-0,efitype=4m,size=4M
ide2: none,media=cdrom
machine: q35
memory: 512
meta: creation-qemu=10.1.2,ctime=1773317123
name: openwrt
net0: virtio=BC:24:11:F2:28:B0,bridge=vmbr0,firewall=1
numa: 0
ostype: l26
scsi0: local-lvm:base-200-disk-1,iothread=1,size=124M,ssd=1
scsihw: virtio-scsi-single
smbios1: uuid=64eaa67b-ad85-4d19-810c-0ada29402606
sockets: 1
template: 1
vmgenid: 04cca8b6-bf4d-4867-a7a2-b7099a69c659
```

- **普通服务器**

```conf
agent: 1
balloon: 2048
bios: ovmf
boot: order=scsi0;ide2;net0
cicustom: user=local:snippets/rocky-10.yaml
cores: 4
cpu: x86-64-v3
efidisk0: local-lvm:base-100-disk-1,efitype=4m,size=4M
ide0: local-lvm:vm-100-cloudinit,media=cdrom
ide2: none,media=cdrom
machine: q35
memory: 4096
meta: creation-qemu=10.1.2,ctime=1772954179
name: rocky-10
net0: virtio=BC:24:11:BF:86:5C,bridge=vmbr0,firewall=1
numa: 0
ostype: l26
rng0: source=/dev/urandom
scsi0: local-lvm:vm-100-disk-0,discard=on,iothread=1,size=64G,ssd=1
scsihw: virtio-scsi-single
smbios1: uuid=58bea02e-ec2a-4067-a473-65285fae4291
sockets: 1
template: 1
vmgenid: c8a35edd-b18b-43f8-a66d-b97be5122470
```
