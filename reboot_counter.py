import os

def check_reboot_count():
    count = read_reboot_count()
    if count > 3:
        return False
    else:
        return True

def read_reboot_count():
    if os.path.exists("reboot.count"):
        with open("reboot.count", "r") as reboot_count_file:
            try:
                reboot_count = reboot_count_file.read()
                reboot_count = int(reboot_count)
                return reboot_count
            except ValueError as e:
                os.remove("reboot.count")
                return -1
    else:
        return -1

def write_reboot_count(count):
    reboot_count = read_reboot_count()

    if reboot_count != -1:
        os.remove("reboot.count")

    with open("reboot.count", "w") as reboot_count_file:
        if count == 0:
            print("removing")
            os.remove("reboot.count")
        else:
            reboot_count = int(reboot_count)
            reboot_count += 1
            reboot_count_file.write(str(reboot_count))