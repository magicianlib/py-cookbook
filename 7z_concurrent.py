import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def compress_one(f: Path, password="001", dry_run=True):
    archive = f.with_name(f.name + ".7z")
    cmd = ["7z", "a", f"-p{password}", "-mhe", "-sdel", str(archive), str(f)]

    if dry_run:
        return f, archive, 0, "[干跑] " + " ".join(cmd)

    print("[运行] " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f, archive, result.returncode, result.stderr


def compress_all(workdir=".", password="001", workers=4, dry_run=True):
    workdir = Path(workdir)
    if not workdir.is_dir():
        print(f"[错误] 不是有效目录: {workdir}")
        return

    # 当前脚本自身的绝对路径，用于排除
    try:
        self_path = Path(__file__).resolve()
    except NameError:
        self_path = None

    files = [
        f for f in workdir.iterdir()
        if f.is_file()
           and f.suffix != ".7z"
           and (self_path is None or f.resolve() != self_path)
    ]

    if not files:
        print("[提示] 没有需要处理的文件")
        return

    if dry_run:
        print(f"[干跑] 将处理 {len(files)} 个文件：")
        for f in files:
            archive = f.with_name(f.name + ".7z")
            print(f"  {f.name} -> {archive.name}")
        print("[干跑完成]")
        print("    确认没问题可使用 --run 参数运行")
        print("    详细用法可使用 --help 查看")
        return

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(compress_one, f, password, dry_run): f for f in files}

        for fut in as_completed(futures):
            f, archive, code, err = fut.result()
            if code == 0:
                print(f"[完成] {f.name} -> {archive.name}")
            else:
                print(f"[失败] {f.name}: {err.strip()}")


def main():
    parser = argparse.ArgumentParser(description="批量用 7z 加密压缩目录下的文件")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="要处理的目录（默认当前目录）",
    )
    parser.add_argument("-p", "--password", default="001", help="压缩密码（默认 001）")
    parser.add_argument("-w", "--workers", type=int, default=4, help="并行数（默认 4）")
    parser.add_argument("--run", action="store_true", help="真正执行（默认只干跑）")
    args = parser.parse_args()

    compress_all(
        workdir=args.directory,
        password=args.password,
        workers=args.workers,
        dry_run=not args.run,
    )


if __name__ == "__main__":
    main()
