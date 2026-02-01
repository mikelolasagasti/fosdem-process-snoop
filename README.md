# process-snoop

A demonstration eBPF tool showcasing how to package CO-RE (Compile Once, Run Everywhere) eBPF programs for Linux distributions.

## About

This repository contains a minimal eBPF application that monitors process execution using tracepoints. It serves as a practical example for the FOSDEM 2026 talk:

**[Packaging eBPF Programs in a Linux Distribution: Challenges & Solutions](https://fosdem.org/2026/schedule/event/VSXPA8-packaging-ebpf-in-linux-distros/)**

*FOSDEM 2026 · Distributions Devroom · Sunday, February 1, 2026*

## What It Does

`process-snoop` is a pure CO-RE eBPF tool that logs every command executed on the system by attaching to the `sys_enter_execve` tracepoint. It demonstrates:

- **CO-RE compatibility**: Works across different kernel versions without recompilation
- **Minimal dependencies**: Only requires `libbpf` at runtime (no Clang/LLVM needed)

## Repository Contents

- `agent.bpf.c` - The eBPF program (kernel-side code)
- `main.c` - The userspace loader using libbpf
- `process-snoop.spec` - RPM spec file demonstrating the packaging approach

## Creating the Source Tarball

The RPM spec file expects the source files to be in a `process-snoop-1.0` directory. To create the tarball:

```bash
mkdir -p process-snoop-1.0
cp agent.bpf.c main.c process-snoop-1.0/
tar czf process-snoop-1.0.tar.gz process-snoop-1.0/
```

The resulting `process-snoop-1.0.tar.gz` can then be used with `rpmbuild` or uploaded to COPR.

## Building

See `process-snoop.spec` for the complete build process. The key steps are:

1. Compile the eBPF program with Clang
2. Generate the skeleton header with `bpftool`
3. Compile the userspace loader

## Runtime Requirements

- Linux kernel with BTF support (Fedora 30+, RHEL 8.2+)
- `libbpf` library
- `CAP_BPF` and `CAP_PERFMON` capabilities

## COPR Builds

Pre-built packages are available via COPR for multiple distributions:

**[COPR: mikelo2/process-snoop](https://copr.fedorainfracloud.org/coprs/mikelo2/process-snoop/)**

Supported distributions:
- Fedora Rawhide
- Fedora 43
- Fedora 42
- EPEL 10
- EPEL 9
- EPEL 8

To install from COPR:

```bash
dnf copr enable mikelo2/process-snoop
dnf install process-snoop
```

## License

GPLv2

## Related Links

- [FOSDEM 2026 Session](https://fosdem.org/2026/schedule/event/VSXPA8-packaging-ebpf-in-linux-distros/)
- [Fedora eBPF SIG](https://fedoraproject.org/wiki/SIGs/eBPF)
