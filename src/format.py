import argparse
import asyncio
import curses
import os
import subprocess

import ascii_art


def print_feedback_with_bubble(feedback: dict) -> None:
    for file, result in feedback.items():
        lines = result.split('\n')
        max_length = max(len(line) for line in lines)
        bubble_top = " " + "_" * (max_length + 2)
        bubble_middle = [f"< {line.ljust(max_length)} |" for line in lines]
        bubble_bottom = " " + "-" * (max_length + 2)

        print(f"File: {file}")
        print(bubble_top)
        for line in bubble_middle:
            print(line)
        print(bubble_bottom)
        print("\n")


async def animate_ascii_art(stdscr, art_1: str, art_2: str, art_3: str) -> None:
    width = 20
    speed = 0.5
    curses.curs_set(0)
    stdscr.clear()

    while not stop_animation.is_set():
        max_y, max_x = stdscr.getmaxyx()

        # ASCIIアートがターミナルに収まるかを確認
        if len(art_1.splitlines()) > max_y or width > max_x:
            stdscr.clear()
            stdscr.addstr(0, 0, "terminal size is too small!")
            stdscr.refresh()
            await asyncio.sleep(10)
            continue

        stdscr.clear()
        for j, line in enumerate(art_1.splitlines()):
            stdscr.addstr(j, width // 2, line)
        stdscr.refresh()
        await asyncio.sleep(speed)

        stdscr.clear()
        for j, line in enumerate(art_2.splitlines()):
            stdscr.addstr(j, width // 2, line)
        stdscr.refresh()
        await asyncio.sleep(speed)

        stdscr.clear()
        for j, line in enumerate(art_3.splitlines()):
            stdscr.addstr(j, width // 2, line)
        stdscr.refresh()
        await asyncio.sleep(speed)


async def run_ruff_check(target_dir: str, sleep_time: int) -> dict[str, str]:
    feedback = dict()

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # 非同期で Ruff を実行
                process = await asyncio.create_subprocess_exec(
                    'ruff', 'check', file_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                stdout, stderr = await process.communicate()

                if sleep_time:
                    await asyncio.sleep(sleep_time)

                # 修正箇所がない場合は"デレ"
                feedback[file_path] = "Просто ужасно" if process.returncode == 0 else f"{
                    stdout.decode()} \n"

    # チェックが終了したらアニメーションを停止
    stop_animation.set()

    return feedback


async def main(target_dir: str, sleep_time: int) -> None:
    global stop_animation
    stop_animation = asyncio.Event()
    ascii_art_normal = ascii_art.normal_437
    ascii_art_left = ascii_art.left_437
    ascii_art_right = ascii_art.right_437

    # cursesの初期化
    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        # アニメーションを動かすタスクを作成
        animation_task = asyncio.create_task(animate_ascii_art(
            stdscr, ascii_art_normal, ascii_art_left, ascii_art_right))

        # ruff のチェックを非同期で実行
        feedback = await run_ruff_check(target_dir, sleep_time)

        # アニメーションタスクを待機
        await animation_task

    finally:
        # ターミナルを解放
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

        print_feedback_with_bubble(feedback)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Specify the target directory for Ruff checks and the time interval between each check.')
    parser.add_argument('target_dir', type=str, help='Directory to be checked')
    parser.add_argument('sleep_time', type=float,
                        help='Time (in seconds) to wait between each Ruff check')

    args = parser.parse_args()

    asyncio.run(main(args.target_dir, args.sleep_time))
