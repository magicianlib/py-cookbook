import argparse
import subprocess
from pathlib import Path


def compress_all(workdir=".", password="001", dry_run=True):
    workdir = Path(workdir)
    if not workdir.is_dir():
        print(f"[错误] 不是有效目录: {workdir}")
        return

    try:
        self_path = Path(__file__).resolve()
    except NameError:
        self_path = None

    for f in sorted(workdir.iterdir()):
        if not f.is_file():
            continue
        if f.suffix == ".7z":
            continue
        if self_path is not None and f.resolve() == self_path:
            print(f"[跳过] 当前脚本 {f.name}")
            continue

        # a.txt -> a.txt.7z
        archive = f.with_name(f.name + ".7z")
        cmd = ["7z", "a", f"-p{password}", "-mhe", "-sdel", str(archive), str(f)]

        if dry_run:
            print("[干跑]", " ".join(cmd))
            continue

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[完成] {f.name} -> {archive.name}")
        else:
            print(f"[失败] {f.name}: {result.stderr.strip()}")


def main():
    parser = argparse.ArgumentParser(description="批量用 7z 加密压缩目录下的文件")
    parser.add_argument(
        "directory",
        nargs="?",  # 可选参数
        default=".",  # 不传就用当前目录
        help="要处理的目录（默认当前目录）",
    )
    parser.add_argument("-p", "--password", default="001", help="压缩密码（默认 001）")
    parser.add_argument("--run", action="store_true", help="真正执行（默认只干跑）")

    args = parser.parse_args()
    dry_run = not args.run

    compress_all(
        workdir=args.directory,
        password=args.password,
        dry_run=dry_run,
    )

    if dry_run:
        print("[干跑完成]")
        print("    确认没问题可使用 --run 参数运行")
        print("    详细用法可使用 --help 查看")


if __name__ == "__main__":
    main()
