import apis

isp = apis.check_isp_with_retries()
print(f"ISP: {isp}")