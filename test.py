import speedtest

def run_speed_test():
    # Create a Speedtest object
    st = speedtest.Speedtest()

    # Get download speed in bits per second
    download_speed = st.download()

    # Get upload speed in bits per second
    upload_speed = st.upload()

    # Convert speeds to more human-readable units
    download_speed_mbps = download_speed / 10**6
    upload_speed_mbps = upload_speed / 10**6

    # Print the results
    print(f"Download Speed: {download_speed_mbps:.2f} Mbps")
    print(f"Upload Speed: {upload_speed_mbps:.2f} Mbps")

if __name__ == "__main__":
    # Run the speed test
    run_speed_test()
