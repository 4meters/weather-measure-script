import os

def check_sds011_reset_count():
    count = read_sds011_reset_count()
    if count > 3:
        return False
    else:
        return True

def read_sds011_reset_count():
    if os.path.exists("reset-sds011.count"):
        with open("reset-sds011.count", "r") as reboot_count_file:
            try:
                reboot_count = reboot_count_file.read()
                reboot_count = int(reboot_count)
                return reboot_count
            except ValueError as e:
                os.remove("reset-sds011.count")
                return -1
    else:
        return -1

def write_sds011_reset_count(count):
    reboot_count = read_sds011_reset_count()

    if reboot_count != -1:
        os.remove("reset-sds011.count")

    with open("reset-sds011.count", "w") as reboot_count_file:
        if count == 0:
            #print("removing sds011 reset counter file")
            os.remove("reset-sds011.count")
        else:
            reboot_count = int(reboot_count)
            reboot_count += 1
            reboot_count_file.write(str(reboot_count))