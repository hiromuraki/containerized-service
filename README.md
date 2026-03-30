# 个人服务部署方案

## 1. 目录结构

- **oci-image**: 容器镜像
- **quadlet**: Quadlet 服务
- **cloud-init**: 云镜像自动部署配置

## 2. 默认端口占用

- **Forgejo**
  - 3000: 主站点
  - 2222: Git SSH

- **Vaultwarden**
  - 3010: 主站点

- **Drawio**
  - 3020: 主站点

- **Excalidraw**
  - 3030: 主站点
  - 3031: 协同服务器

- **Plant UML**
  - 3040: 主站点

## 3. 服务拉起

```bash
systemctl --user restart drawio-pod
systemctl --user restart forgejo-pod
systemctl --user restart caddy-pod
systemctl --user restart vaultwarden-pod
systemctl --user restart excalidraw-pod
```

## 4. KVM 配置建议

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
