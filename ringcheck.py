import re
import subprocess
import time

def monitor_journal(threshold, cooldown_seconds, ignore_delay, pre_trigger_delay):
    """
    threshold: if ring_number < threshold, we consider a trigger.
    cooldown_seconds: minimum wait between consecutive triggers.
    ignore_delay: how long to ignore logs (by killing journal) after triggering.
    pre_trigger_delay: how long to wait right before triggering nextring.bash.
    """
    pattern = re.compile(r'"ring":(\d+)')
    last_trigger_time = 0

    while True:
        # Start a new journalctl process, reading logs from 'now' forward.
        process = subprocess.Popen(
            ['journalctl', '-u', 'para.service', '--no-hostname', '--since=now', '-f'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            for line in process.stdout:
                match = pattern.search(line)
                if not match:
                    continue

                ring_number = int(match.group(1))
                print(f"Detected ring: {ring_number}")

                # Check if ring_number < threshold
                if ring_number < threshold:
                    now = time.time()
                    if now - last_trigger_time >= cooldown_seconds:
                        print(f"[INFO] ring {ring_number} < threshold {threshold}. Cooldown passed.")
                        print(f"[INFO] Waiting {pre_trigger_delay}s before triggering nextring.bash...")
                        # -------------------------
                        # PRE-TRIGGER DELAY ADDED
                        # -------------------------
                        time.sleep(pre_trigger_delay)

                        print("[INFO] Triggering /root/nextring.bash now.")
                        subprocess.run(['/root/nextring.bash'])

                        last_trigger_time = time.time()

                        # Stop reading logs so we skip any that appear during the ignore window
                        print("[INFO] Stopping journal monitoring now.")
                        process.terminate()
                        process.wait()

                        print(f"[INFO] Sleeping {ignore_delay} seconds; logs are completely ignored in this period.")
                        time.sleep(ignore_delay)

                        # Break so we restart journalctl fresh after ignore_delay
                        break
                    else:
                        remain = cooldown_seconds - (now - last_trigger_time)
                        print(f"[INFO] Cooldown not reached. {remain:.1f}s remaining.")
            else:
                # If we exit the for-loop without a break (journal ended or no new lines):
                time.sleep(1)

        except Exception as e:
            print("[ERROR]", e)

        finally:
            # Ensure the process is terminated if it's still running
            if process.poll() is None:
                process.terminate()
                process.wait()
        # Loop repeats: after ignore_delay, we reattach to 'journalctl --since=now'.

if __name__ == "__main__":
    THRESHOLD_VALUE = 2
    COOLDOWN_SECONDS = 120  # how long between triggers
    IGNORE_DELAY = 120       # how long to ignore logs after trigger
    PRE_TRIGGER_DELAY = 60  # how long to wait before actually triggering

    monitor_journal(THRESHOLD_VALUE, COOLDOWN_SECONDS, IGNORE_DELAY, PRE_TRIGGER_DELAY)
